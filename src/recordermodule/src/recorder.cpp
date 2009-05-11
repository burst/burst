#include <sys/time.h>
#include <time.h>
#include <iostream>
#include <fstream>
#include <vector>

#include "alproxy.h"
#include "almemoryproxy.h"

#include "recorder.h"


using namespace std;
using namespace AL;

const char* VARNAMES_FILENAME = "/home/root/recorder_vars.txt";
const char* RESULTS_DIRECTORY = "/media/userdata/"  ;

//______________________________________________
// constructor
//______________________________________________
recorder::recorder (ALPtr < ALBroker > pBroker, std::string pName):ALModule (pBroker,
	  pName), m_recording(false), m_broker(pBroker), m_file_init(false), m_row(-42)
{

    std::cout << "recorder::recorder: Hello" << std::endl;
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
  try
  {
    m_log = getParentBroker ()->getLoggerProxy ();
    //log->logInFile(true, "test.txt", "lowinfo");
  }
  catch (ALError & e)
  {
    std::cout << "could not create a proxy to ALLogger module" << std::endl;
  }

  //Create a proxy on memory module
  try
  {
    m_memory = getParentBroker ()->getMemoryProxy ();
  }
  catch (ALError & e)
  {
    std::cout << "could not create a proxy to ALMemory module" << std::endl;
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

  // read the variable names we will be writing to a csv file
    ifstream varfile(VARNAMES_FILENAME);

    if (!varfile.is_open()) {
        std::cout << "ERROR: cannot find the variable files - no recording done. where is /home/root/recorder_vars.txt?" << std::endl;
        return;
    }

    while (!varfile.eof()) {
        std::string line;
        getline(varfile, line);
        if (line.size() <= 1) {
            continue;
        }
        m_varnames.push_back(line); // TODO - algorithms, copy?
    }
    varfile.close();
    std::cout << "recorder::recorder: read " << m_varnames.size() << " variable names" << std::endl;

}

std::string get_date() {
   time_t t = time(0);
   struct tm* lt = localtime(&t);
   char time_str[15];
   sprintf(time_str, "%04d%02d%02d_%02d%02d%02d", lt->tm_year + 1900, lt->tm_mon+ 1, lt->tm_mday, lt->tm_hour, lt->tm_min, lt->tm_sec);
   return std::string(time_str);
}


//______________________________________________
// startRecording
//______________________________________________
void recorder::startRecording ()
{
  this->m_recording = true;
  this->m_row = 0;
    if (!m_file_init) {

        m_filename = std::string(RESULTS_DIRECTORY) + "/recorder_" + get_date() + ".csv.gz";
        std::cout << "recorder: opening file " << m_filename << std::endl;
        // open the file
        m_file_out.open(m_filename.c_str());
        m_file_init = true;
    }

    int i = 0;
  try
  {
    std::cout << "recorder: start: initialization has begun" << std::endl;
    this->m_memory =
      ALPtr < AL::ALMemoryProxy > (getParentBroker ()->getMemoryProxy ());

    const std::string & strModuleName = getName ().c_str ();
    std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time";

    m_memory->subscribeOnDataChange (memoryKeyNameValueChangesEveryCycle,	// the key
				   strModuleName,	// the name of this module
				   string ("CycleChangedNotification"),	// the name of the notification
				   string ("dataChanged"));	// the method to use for the callback

    // make sure we get notifications every change of value. The default would have been every 50ms
    m_memory->subscribeOnDataSetTimePolicy (memoryKeyNameValueChangesEveryCycle,
					  strModuleName, 0);

    m_memoryfastaccess =
        AL::ALPtr<ALMemoryFastAccess >(new ALMemoryFastAccess());

    m_memoryfastaccess->ConnectToVariables(m_broker, m_varnames);
    m_values.resize(m_varnames.size(), 0.0); // init m_values

    std::cout << "recorder task started." << std::endl;

  } catch (AL::ALError e)
  {
    std::cout << "Failed to start the recorder task: " << e.
      toString () << std::endl;
    std::cout << "last value for i: " << i << std::endl;
  }
}


//______________________________________________
// stopRecording
//______________________________________________
void recorder::stopRecording ()
{
    this->m_recording = false;
  try
  {
    const std::string & strModuleName = getName ().c_str ();

    std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time";	// We could also use "Motion/Synchro"
    m_memory->unsubscribeOnDataChange (memoryKeyNameValueChangesEveryCycle,
				     string (strModuleName));

    std::cout << "recorder: task stopped. closing file." << std::endl;

    if (m_file_init) {
        std::cout << "recorder: closing file" << std::endl;
        // close the file
        m_file_out.close();
        m_file_init = false;
    }
    std::cout << "recorder: file closed" << std::endl;
  } catch (AL::ALError e)
  {
    std::cout << "Failed to stop the recorder task: " << e.
      toString () << std::endl;
  }

}


//______________________________________________
// version
//______________________________________________
int recorder::getRowNumber ()
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
  if (!m_recording || !m_file_init) return;
  try
  {
    m_row += 1;
    if (m_row % PRINT_DECIMATION == 0) {
        std::cout << "recorder: num_calls == " << m_row << std::endl;
    }

    m_memoryfastaccess->GetValues(m_values);
    int size = m_values.size();
    if (m_row % PRINT_DECIMATION == 0) {
        std::cout << "recorder: m_values.size() == " << size << ">>>" << std::endl;
    }
    for (int i = 0 ; i < size ; i++) {
        m_file_out << m_values[i] << ",";
        if (m_row % PRINT_DECIMATION == 0) {
            std::cout << m_values[i] << ", ";
        }
    }
    if (m_row % PRINT_DECIMATION == 0) {
        std::cout << "<<<" << std::endl;
    }
    m_file_out << "\n";

  } catch (AL::ALError e)
  {
    std::cout << "Recorder caught ALError: " << e.toString () << std::endl;
  }
}

