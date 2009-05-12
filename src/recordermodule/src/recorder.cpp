#include <sys/time.h>
#include <time.h>
#include <iostream>
#include <fstream>
#include <vector>

#include <cstdio>

#include "alproxy.h"
#include "almemoryproxy.h"

#ifndef USE_PROCESS
# ifdef USE_ZLIB_DIRECTLY
#include "gzlog.h"
# endif
#endif

#include "burstutil.h"

#include "recorder.h"

// Turn on for verbose debug logs - read with nao log
//#define DEBUG_RECORDING

using namespace std;
using namespace AL;

const char *VARNAMES_FILENAME = "/home/root/recorder_vars.txt";
const char *RESULTS_DIRECTORY = "/media/userdata";

//______________________________________________
// constructor
//______________________________________________
recorder::recorder (ALPtr < ALBroker > pBroker, std::string pName):ALModule (pBroker,
          pName), m_recording (false), m_broker (pBroker),
m_file_init (false), m_row (-42)
{

    std::cout << "recorder: Module starting" << std::endl;
    // Describe the module here
    setModuleDescription
        ("This is the recorder module - designed to record a lot of stuff to a csv file, that's all.");

    // Define callable methods with there description
    functionName ("startRecording", "recorder", "start recording a csv file");
    BIND_METHOD (recorder::startRecording);

    functionName ("getRowNumber", "recorder", "return number of row");
    BIND_METHOD (recorder::getRowNumber);

    functionName ("stopRecording", "recorder", "stop recording the csv file");
    BIND_METHOD (recorder::stopRecording);

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
    }
    catch (ALError & e) {
        std::
            cout << "could not create a proxy to ALMemory module" <<
            std::endl;
    }

/*
    try
    {
        dcm =  AL::ALPtr<AL::DCMProxy>(new AL::DCMProxy(broker));
    }
    catch (ALError & e)
    {
        std::cout << "could not create a proxy to DCM module" << std::endl;
    }
    */
}

// Allow user to change the file while running - reread every time we startRecording
void recorder::readVariablesFile()
{
    ::readVariablesFile(VARNAMES_FILENAME, m_varnames);
    std::cout << "recorder: read " << m_varnames.size () <<
        " variable names" << std::endl;

    m_values.resize (m_varnames.size (), 0.0);      // init m_values
    m_values_size = m_values.size();
}

#ifdef USE_ZLIB_DIRECTLY
void recorder::openZlibFile()
{
    // open the regular file too
    m_file_out = fopen(m_filename.c_str(), "w+");

    // init the zlib stream (actually, this function is misnamed)
    int level = Z_DEFAULT_COMPRESSION; // compression level
    /* allocate deflate state */
    m_strm.zalloc = Z_NULL;
    m_strm.zfree = Z_NULL;
    m_strm.opaque = Z_NULL;
    ret = deflateInit2(&m_strm, level); // deflateInit2 creates a gzip file, not zlib headers
    if (ret != Z_OK) {} // TODO -report error
}

void recorder::writeSingleStringToFile(const std::string& inp)
{
#define CHUNK 16384
    static char out[CHUNK];
    int len = inp.size();
    strm.avail_out = CHUNK;
    strm.next_out = out;
    strm.next_in = inp.c_str();
    do {
        deflate(&m_strm, Z_NO_FLUSH); // Z_FINISH?
        int have = CHUNK - strm.avail_out;
        fwrite(out, 1, have, m_file_out);
    } while (strm.avail_out == 0);
#undef CHUNK
}

void recorder::closeZlibFile()
{
    deflateEnd(&m_strm);

}

#endif // USE_ZLIB_DIRECTLY

//______________________________________________
// startRecording - Can be called multiple times
// during the lifetime of the module, but only
// has an effect after stopRecording (or on start).
// saves to a new filename everytime (unless you
// call it multiple times a second, it will work
// but overwrite the last one in that second).
//
// TODO
// uses a new ALMemoryFastAccess every time - is
// that ok?
//______________________________________________
void
recorder::startRecording ()
{
    if (this->m_recording) return;

    readVariablesFile();

    if (this->m_values_size == 0) {
        std::cout << "recorder: not starting, number of values to record is zero" << std::endl;
        return;
    }

    this->m_recording = true;
    this->m_row = 0;
    if (!m_file_init) {

        m_filename =
            std::string (RESULTS_DIRECTORY) + "/recorder_" + get_date () +
            ".csv.gz";
#ifdef USE_PROCESS
        // create the process
        std::cout << "recorder: creating subprocess gzip > " << m_filename << std::endl;
        std::string cmd = std::string("gzip > ") + m_filename;
        this->m_file_out = popen(cmd.c_str(), "w");
#else
        // open the file
        std::cout << "recorder: opening file " << m_filename << std::endl;
# ifdef USE_ZLIB_DIRECTLY
        this->openZlibFile();
# else
        //m_file_out = gzlog_open(.open (m_filename.c_str ());
        m_file_out.open(m_filename.c_str());
# endif
#endif // USE_PROCESS
        m_file_init = true;
    }

    try {
        std::cout << "recorder: start: initialization has begun" << std::endl;
        this->m_memory =
            ALPtr < AL::ALMemoryProxy >
            (getParentBroker ()->getMemoryProxy ());

        const std::string & strModuleName = getName ().c_str ();
        std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time";

        m_memory->subscribeOnDataChange (memoryKeyNameValueChangesEveryCycle,   // the key
                                         strModuleName, // the name of this module
                                         string ("CycleChangedNotification"),   // the name of the notification
                                         string ("dataChanged"));       // the method to use for the callback

        // Following two lines cause us to be called 50Hz. Without them it is more like 16Hz (60ms)
        //m_memory->subscribeOnDataSetTimePolicy
        //    (memoryKeyNameValueChangesEveryCycle, strModuleName, 0);

        m_memoryfastaccess =
            AL::ALPtr < ALMemoryFastAccess > (new ALMemoryFastAccess ());

        m_memoryfastaccess->ConnectToVariables (m_broker, m_varnames);

        std::cout << "recorder: task started." << std::endl;

    } catch (AL::ALError e) {
        std::cout << "recorder: Failed to start the task: " << e.toString () <<
            std::endl;
    }
}


//______________________________________________
// stopRecording
//______________________________________________
void
recorder::stopRecording ()
{
    if (!this->m_recording) return;

    this->m_recording = false;
    try {
        const std::string & strModuleName = getName ().c_str ();

        std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time";   // We could also use "Motion/Synchro"
        m_memory->unsubscribeOnDataChange
            (memoryKeyNameValueChangesEveryCycle, string (strModuleName));

        std::cout << "recorder: task stopped. closing file." << std::endl;

    }
    catch (AL::ALError e) {
        std::cout << "recorder: Failed to stop the task: " << e.toString () <<
            std::endl;
    }

    if (m_file_init) {
#ifdef USE_PROCESS
        std::cout << "recorder: closing gzip process" << std::endl;
        pclose(m_file_out);
#else
        std::cout << "recorder: closing file" << std::endl;
        // close the file
# ifdef USE_ZLIB_DIRECTLY
        this->closeZlibFile();
# else
        m_file_out.close ();
# endif
#endif // USE_PROCESS
        m_file_init = false;
    }
    std::cout << "recorder: file closed" << std::endl;
}


//______________________________________________
// version
//______________________________________________
int
recorder::getRowNumber ()
{
    return m_row;
}


//______________________________________________
// version
//______________________________________________
std::string recorder::version ()
{
    return ALTOOLS_VERSION (RECORDERMODULE);
}


//______________________________________________
// destructor
//______________________________________________
recorder::~recorder ()
{

}

#ifdef USE_PROCESS
void recorder::writeToFile()
{
#ifndef RECORDER_DO_NOTHING
        for (int i = 0; i < m_values_size; i++) {
            fprintf(m_file_out, "%f,", m_values[i]);
        }
        fprintf(m_file_out, "\n");
#endif // RECORDER_DO_NOTHING
}

#else
void recorder::writeToFile()
{
#ifndef RECORDER_DO_NOTHING
        for (int i = 0; i < m_values_size; i++) {
            m_file_out << m_values[i] << ",";
        }
        m_file_out << "\n";
#endif
}
#endif // USE_PROCESS

/**
 * dataChanged. Called by ALMemory when subcription
 * has been modified.
 * @param pDataName, name of the suscribed data
 * @param pValue, value of the suscribed data
 * @param pMessage, message written by user during suscription
 */
void
recorder::dataChanged (const std::string & pDataName, const ALValue & pValue,
                       const std::string & pMessage)
{
    const int PRINT_DECIMATION = 100;
    if (!m_recording || !m_file_init)
        return;
    try {
        m_row += 1;
        if (m_row % PRINT_DECIMATION == 0) {
            std::cout << "recorder: num_calls == " << m_row << std::endl;
        }

        m_memoryfastaccess->GetValues (m_values);

        if (m_row % PRINT_DECIMATION == 0) {
            std::cout << "recorder: m_values.size() == " << m_values_size <<
                std::endl;
        }
        this->writeToFile();
#ifdef DEBUG_RECORDING
        for (int i = 0; i < m_values_size; i++) {
            if (m_row % PRINT_DECIMATION == 0) {
                std::cout << m_values[i] << ", ";
            }
        }
        if (m_row % PRINT_DECIMATION == 0) {
            std::cout << std::endl;
        }
#endif

    }
    catch (AL::ALError e) {
        std::cout << "Recorder caught ALError: " << e.toString () << std::
            endl;
    }
}

