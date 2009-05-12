#include <sys/time.h>
#include <time.h>
#include <iostream>
#include <fstream>
#include <vector>

#include <cstdio>

#include "alproxy.h"
#include "almemoryproxy.h"

#include "burstmem.h"

using namespace AL;

//______________________________________________
// constructor
//______________________________________________
burstmem::burstmem (ALPtr < ALBroker > pBroker, std::string pName):ALModule (pBroker,
          pName)
{

    std::cout << "burstmem: Module starting" << std::endl;
    // Describe the module here
    setModuleDescription
        ("This is the burstmem module - designed to record a lot of stuff to a csv file, that's all.");

    // Define callable methods with there description
    //functionName ("startRecording", "burstmem", "start recording a csv file");
    //BIND_METHOD (burstmem::startRecording);

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

}

//______________________________________________
// version
//______________________________________________
std::string burstmem::version ()
{
    // I messed up the copy/rename of recordermodule, this doen't compile,
    // missing some symbols
    //return ALTOOLS_VERSION (BURSTMEMMODULE);
    return "burstmem";
}


//______________________________________________
// destructor
//______________________________________________
burstmem::~burstmem ()
{

}

