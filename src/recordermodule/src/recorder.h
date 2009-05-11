/**
 * @author Eran Polosetski (NOT)
 * BURST 2009 - recorder module
 *
 */

#ifndef recorder_H
# define recorder_H

#include <vector>
#include <string>

#include "recordermodule.h"
#include "alloggerproxy.h"
#include "almemoryproxy.h"
#include "alptr.h"
#include "almemoryfastaccess.h"

#include "gzstream.h"

using namespace AL;

class recorder:public
  AL::ALModule
{
public:
    /**
     * Default Constructor.
     */
  recorder (ALPtr < ALBroker > pBroker, std::string pName);

    /**
     * Destructor.
     */
  virtual ~
  recorder ();

    // External module interface
    void startRecording();

    void stopRecording();

    int getRowNumber();
  
    /**
     * version
     * @return The version number of recorder
     */
  std::string
  version ();


    /**
     * innerTest
     * @return True if all the tests passed
     */
  bool
  innerTest ()
  {
    return true;
  };


  void
  dataChanged (const std::string & pDataName, const ALValue & pValue,
	       const std::string & pMessage);

private:
    
    ogzstream                     m_file_out;
    std::string                   m_filename;
    bool                          m_file_init;   // true if m_fileout is open, false otherwise
    bool                          m_recording;   // are we recording
    int                           m_row;         // which row of the csv file has been recorded

    AL::ALPtr<AL::ALBroker>       m_broker;      // needed for ConnectToVariables
    std::vector<std::string>      m_varnames;
    std::vector<float>            m_values;
    AL::ALPtr<ALMemoryFastAccess> m_memoryfastaccess;

  //proxy to the logger module
  ALPtr < AL::ALLoggerProxy > m_log;

  //proxy to the memory module
  ALPtr < AL::ALMemoryProxy > m_memory;


};
#endif // recorder_H
