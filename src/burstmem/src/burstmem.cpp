#include <sys/time.h>
#include <time.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>


#include <cstdio>

#include <sys/mman.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h> // O_WRONLY
#include <stdlib.h>

#include "alproxy.h"
#include "almemoryproxy.h"

#include "burstutil.h"
#include "burstmem.h"

using namespace AL;

// TODO - read these from config.h which somehow gets created through python
// during startup using the values in lib/burst/consts.py
const char* CHARGER_CONFIG_FILENAME = "/home/root/burst/lib/etc/charger_warning.txt";
const char* MMAP_FILENAME           = "/home/root/burst/lib/etc/burstmem.mmap";
const unsigned int MMAP_LENGTH      = 4096;

const int SONAR_MMAP_SLOTS = 2; // left and right sonar, two floats.

const int burstmem::CHARGER_UNKNOWN = 0,
    burstmem::CHARGER_CONNECTED = 1,
    burstmem::CHARGER_DISCONNECTED = 2;

//______________________________________________
// constructor
//______________________________________________
burstmem::burstmem (ALPtr < ALBroker > pBroker, std::string pName)
    : ALModule (pBroker, pName), m_copying(false), m_memory_mapped(false)
    , m_mmap(NULL)
    , lastBatteryStatus(CHARGER_UNKNOWN)
{

    std::cout << "burstmem: Module starting" << std::endl;
    // Describe the module here
    setModuleDescription
        ("This is the burstmem module - designed to record a lot of stuff to a csv file, that's all.");

    // Define callable methods with there description
    functionName ("startMemoryMap", "burstmem", "start copying almemory->mmap periodically");
    BIND_METHOD (burstmem::startMemoryMap);

    functionName ("stopMemoryMap", "burstmem", "stop memcopy and alfast");
    BIND_METHOD (burstmem::stopMemoryMap);

    functionName ("isMemoryMapRunning", "burstmem", "return true if almemory is memory-mapped");
    BIND_METHOD (burstmem::isMemoryMapRunning);

    functionName ("getNumberOfVariables", "burstmem", "return number of read variables (for debugging)");
    BIND_METHOD (burstmem::getNumberOfVariables);

    functionName ("getVarNameByIndex", "burstmem", "return read variable name (for debugging)");
    BIND_METHOD (burstmem::getVarNameByIndex);

    // TODO - setMappedVariables
    functionName ("clearMappedVariables", "burstmem", "clear list of mapped variables");
    BIND_METHOD (burstmem::clearMappedVariables);

    functionName ("addMappedVariable", "burstmem", "add a single variable to mapped vars, we give the index to protect against changes in order (for any reason)");
    addParam("index", "index in shared memory");
    addParam("var", "name of variable exported by ALMemory");
    BIND_METHOD (burstmem::addMappedVariable);

    //Create a proxy on logger module
    try {
        m_log = getParentBroker ()->getLoggerProxy ();
        //log->logInFile(true, "test.txt", "lowinfo");
    }
    catch (ALError & e) {
        std::
            cout << "could not create a proxy to ALLogger module" <<
            std::endl;
    }

    //Create a proxy on memory module
    try {
        m_memory = getParentBroker ()->getMemoryProxy ();
        textToSpeechProxy = getParentBroker()->getProxy("ALTextToSpeech");
    }
    catch (ALError & e) {
        std::
            cout << "could not create a proxy to ALMemory module" <<
            std::endl;
    }

    readBatteryChargerWarningConfig();

    subscribeToDataChange();
}

void burstmem::readBatteryChargerWarningConfig()
{
    std::vector < std::string > charger_config;
    readVariablesFile(CHARGER_CONFIG_FILENAME, charger_config);
    std::cout << "read " << charger_config.size() << " variables from "
              << CHARGER_CONFIG_FILENAME << std::endl;
    numberOfTicksBeforeAnnouncement = atoi(charger_config[0].c_str());
    ticksLastStatusHasHeld = 0;
}

void burstmem::subscribeToDataChange()
{
    // request updates to memory and connect to variables
    try {
        std::cout << "burstmem: start: subscribing to data changes" << std::endl;

        const std::string & strModuleName = getName ().c_str ();
        std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time";

        m_memory->subscribeOnDataChange (
            memoryKeyNameValueChangesEveryCycle,   // the key
            strModuleName, // the name of this module
            string ("CycleChangedNotification"),   // the name of the notification
            string ("dataChanged"));       // the method to use for the callback

        // Following two lines cause us to be called 50Hz.
        // Without them it is more like 16Hz (60ms)

        //m_memory->subscribeOnDataSetTimePolicy
        //    (memoryKeyNameValueChangesEveryCycle, strModuleName, 0);

        std::cout << "burstmem: task started." << std::endl;

    } catch (AL::ALError e) {
        std::cout << "burstmem: Failed to start the task: " << e.toString () <<
            std::endl;
    }
}

//______________________________________________
// clearMappedVariables
//______________________________________________
void burstmem::clearMappedVariables()
{
    m_varnames.clear();
}

//______________________________________________
// addMappedVariable
//______________________________________________
void burstmem::addMappedVariable(int index, std::string var)
{
    m_varnames.resize(index+1);
    m_varnames[index] = var;
}

//______________________________________________
// setMappedVariables - TODO
//______________________________________________
#if 0
void burstmem::setMappedVariables (const std::vector<std::string> varnames)
{
    m_varnames.clear();
    //std::copy(varnames.begin(), varnames.end(), m_varnames.begin());
    std::cout << "burstmem: will record " << m_varnames.size() << " variables" << std::endl;
}
#endif

//______________________________________________
// version
//______________________________________________
std::string burstmem::version ()
{
    // I messed up the copy/rename of recordermodule, this doen't compile,
    // missing some symbols
    //return ALTOOLS_VERSION (BURSTMEMMODULE);
    return "1.2.0-burstmem";
}


//______________________________________________
// get variable name by index
//______________________________________________
std::string burstmem::getVarNameByIndex (int i)
{
    if (this->m_varnames.size() > i && i >= 0)
        return this->m_varnames[i];
    return std::string("ERROR");
}


//______________________________________________
// get number of variables
//______________________________________________
int burstmem::getNumberOfVariables ()
{
    return this->m_varnames.size();
}

//______________________________________________
// destructor
//______________________________________________
burstmem::~burstmem ()
{

}

//______________________________________________
// return true if memory is currently mapped
//______________________________________________
bool burstmem::isMemoryMapRunning ()
{
    //std::cout << "burstmem: isMemoryMapRunning == " << this->m_copying << ", "
    //    << this->m_memory_mapped << std::endl;
    return (this->m_copying && this->m_memory_mapped);
}

//______________________________________________
// start almemoryfast -> memory map
//______________________________________________
void burstmem::startMemoryMap ()
{
    if (this->m_copying) return;

    // Now we get the variables explicitly by setMappedVariables

    if (this->m_varnames.size() == 0) {
        std::cout << "burstmem: not starting, number of values to record is zero"
                  << std::endl;
        return;
    }

    if ((SONAR_MMAP_SLOTS + this->m_varnames.size()) * sizeof(float) > MMAP_LENGTH) {
        std::cout << "burstmem: not starting, memory map file size is not enough,"
         "need " << this->m_varnames.size() * sizeof(float) <<", have "
         << MMAP_LENGTH << std::endl;
    }

    // important - crash GetVariables otherwise
    m_values.resize(m_varnames.size(), 0.0);
    std::cout << "burstmem: using " << m_values.size() << " variables" << std::endl;

    this->m_copying = true;

    // Initialize sonar readings
    try {
        ALPtr<ALProxy> us = this->getParentBroker()->getProxy( "ALUltraSound" );
        ALValue paramUS;
        paramUS.arrayPush( 250 ); // every 250 ms
        us->callVoid( "subscribe", getName(), paramUS );
    } 
    catch (AL::ALError e) {
        std::cout << "burstmem: Failed to subscribe to ALUltraSound: " << e.toString () <<
            std::endl;
    }

    // do memory mapping
    if (!m_memory_mapped) {

        void* start = 0; // don't care
        int offset = 0;  // offset into file
        m_mmap_fd = open(MMAP_FILENAME, O_RDWR | O_NOATIME);

        if (m_mmap_fd == -1) {
            printf("burstmem: error opening mmap file %s\n", MMAP_FILENAME);
            return;
        }

        m_mmap = reinterpret_cast<float*>(mmap(
                start, MMAP_LENGTH, PROT_READ | PROT_WRITE,
                        MAP_SHARED , m_mmap_fd, offset));
        std::cout << "burstmem: got address " << (unsigned long)m_mmap << std::endl;
        if ((long)m_mmap == -1) {
            std::cout << "burstmem: error getting memory map" << std::endl;
            return;
        }

        m_memory_mapped = true;
        std::cout << "burstmem: memory mapped just fine" << std::endl;
    }

}

//______________________________________________
// stop memory map
//______________________________________________
void burstmem::stopMemoryMap ()
{
    if (!this->m_copying) return;

    this->m_copying = false;
    try {
        const std::string & strModuleName = getName ().c_str ();

        std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time";   // We could also use "Motion/Synchro"
        m_memory->unsubscribeOnDataChange
            (memoryKeyNameValueChangesEveryCycle, string (strModuleName));

        std::cout << "burstmem: task stopped." << std::endl;

    }
    catch (AL::ALError e) {
        std::cout << "burstmem: Failed to stop the task: " << e.toString () <<
            std::endl;
    }

    // TODO: unsubscribe to Sonar variables

    if (m_memory_mapped) {
        munmap(m_mmap, MMAP_LENGTH);
        m_memory_mapped = false;
    }
    std::cout << "burstmem: memory unmapped" << std::endl;
}


//______________________________________________
/**
 * dataChanged. Called by ALMemory when subcription
 * has been modified.
 * @param pDataName, name of the suscribed data
 * @param pValue, value of the suscribed data
 * @param pMessage, message written by user during suscription
 */
//______________________________________________
void
burstmem::dataChanged (const std::string & pDataName, const ALValue & pValue,
                       const std::string & pMessage)
{
    if ( numberOfTicksBeforeAnnouncement != 0 )
        checkBatteryStatus();
    updateMemoryMappedVariables();
}

void
burstmem::updateMemoryMappedVariables()
{
    if (!m_copying || !m_memory_mapped || m_varnames.size() == 0) return;

    try {
        // special treatment to sonar vars - we get them as an array,
        // dump the third parameter (a string), and store the two
        // distances in floats
        ALValue distanceUS = m_memory->call<ALValue>( "getData", string("extractors/alultrasound/distances" ) );
        m_mmap[0] = distanceUS[0];
        m_mmap[1] = distanceUS[1];

        m_values = m_memory->getListData(m_varnames);
        // TODO: direct to the memory mapped file (or at least memcpy?)
        for (int i = 0 ; i < m_values.size(); ++i) {
            m_mmap[i + SONAR_MMAP_SLOTS] = m_values[i];
            //std::cout << "value " << i << " = " << m_values[i] << std::endl;
        }
    }
    catch (AL::ALError e) {
        std::cout << "burstmem: caught ALError: " << e.toString () << std::
            endl;
    }
}

//--------------------------------------------------------------------------------
// Battery Checking functions

void
burstmem::checkBatteryStatus ()
{
    const std::string batteryChargerStatusString = "Device/SubDeviceList/Battery/Current/Sensor/Value";
    float result = this->m_memory->getData(batteryChargerStatusString, 0);
    int newBatteryStatus = result < 0.0 ? CHARGER_DISCONNECTED : CHARGER_CONNECTED;
    if ( lastBatteryStatus != newBatteryStatus )
    {
        lastBatteryStatus = newBatteryStatus;
        ticksLastStatusHasHeld = 1;
    }
    else
    {
        if ( ticksLastStatusHasHeld == numberOfTicksBeforeAnnouncement )
            announceChargerChange( newBatteryStatus );
        if (ticksLastStatusHasHeld != numberOfTicksBeforeAnnouncement+1 ) // Prevent integer overflow.
            ticksLastStatusHasHeld += 1;
    }
}

#define ANNOUNCE_CONNECTED 0

void
burstmem::announceChargerChange( int status )
{
    if ( status == CHARGER_CONNECTED && ANNOUNCE_CONNECTED ) {
        textToSpeechProxy->pCall("say", std::string("Connected"));
    } else if ( status == CHARGER_DISCONNECTED ) {
        textToSpeechProxy->pCall("say", std::string("Disconnected"));
    }
}

