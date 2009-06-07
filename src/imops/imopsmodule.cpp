/**
 * \mainpage
 * \section Author
 * @author Patrick de Pas and Olivier Leroy
 *
 * \section Copyright
 * Aldebaran Robotics (c) 2007 All Rights Reserved - This is an example of use.\n
 * Version : $Id$
 *
 * \section Description
 * Module list :  - STMOBJECT_NAME
 */

#include <signal.h>
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

#include "altypes.h"
#include "alxplatform.h"
#include "albrokermanager.h"
#include "alproxy.h"
#include "almemoryproxy.h"

#include "imopsmodule.h"

////////////////////////////////////////////////////////////////////////////////

using namespace AL;

ImopsModule::ImopsModule (ALPtr < ALBroker > pBroker, std::string pName)
    : ALModule (pBroker, pName)
{

    std::cout << "ImopsModule: Module starting" << std::endl;
    // Describe the module here
    setModuleDescription
        ("This is the imops module - does all the image processing");

    // Define callable methods with there description (left for easy copy/paste if required)
    //functionName ("startMemoryMap", "imops", "start copying almemory->mmap periodically");
    //BIND_METHOD (burstmem::startMemoryMap);

    //Create a proxy on memory module
    try {
        m_memory = getParentBroker ()->getMemoryProxy ();
    }
    catch (ALError & e) {
        std::
            cout << "could not create a proxy to ALMemory module" <<
            std::endl;
    }

    subscribeToDataChange();
}

void ImopsModule::subscribeToDataChange()
{
    // request updates to memory and connect to variables
    try {
        std::cout << "imops: start: subscribing to data changes" << std::endl;

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

        std::cout << "imops: task started." << std::endl;

    } catch (AL::ALError e) {
        std::cout << "imops: Failed to start the task: " << e.toString () <<
            std::endl;
    }
}

//______________________________________________
// version
//______________________________________________
std::string ImopsModule::version ()
{
    // I messed up the copy/rename of recordermodule, this doen't compile,
    // missing some symbols
    //return ALTOOLS_VERSION (IMOPSMODULE);
    return "1.2.0-imops";
}

//______________________________________________
// destructor
//______________________________________________
ImopsModule::~ImopsModule ()
{

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
ImopsModule::dataChanged (const std::string & pDataName, const ALValue & pValue,
                       const std::string & pMessage)
{
    try {
        std::cout << "ARE YOU READY YET?? NEED SOME SUSHI??\n";
    }
    catch (AL::ALError e) {
        std::cout << "Recorder caught ALError: " << e.toString () << std::
            endl;
    }
}

////////////////////////////////////////////////////////////////////////////////

using namespace std;

ImopsModule *limops;

#ifdef __cplusplus
extern "C"
{
#else
#error "not in c++?"
#endif


  int _createModule (ALPtr < ALBroker > pBroker)
  {
    // init broker with the main broker instance 
    // from the parent executable
    ALBrokerManager::setInstance (pBroker->fBrokerManager.lock ());
    ALBrokerManager::getInstance ()->addBroker (pBroker);


    // create modules instance
    ALModule::createModule < ImopsModule > (pBroker, "imops");

    return 0;
  }

  int _closeModule ()
  {
    // Delete module instance

    return 0;
  }

# ifdef __cplusplus
}
# endif

