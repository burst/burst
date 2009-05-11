/**
 * @author Eran Polosetski (NOT)
 * BURST 2009 - recorder module
 *
 */

#ifndef recorder_H
# define recorder_H

#include <vector>
#include <string>

#include <cstdio>

#include "recordermodule.h"
#include "alloggerproxy.h"
#include "almemoryproxy.h"
#include "alptr.h"
#include "almemoryfastaccess.h"

// call gzip in a process, let the os handle the buffer in between. no mutex, no ring buffer, nothing.
#define USE_PROCESS

//#define USE_ZLIB_DIRECTLY

#ifdef USE_ZLIB_DIRECTLY
#include <zlib.h>
#else
#include "gzstream.h"
#endif

// Turn off if you want ALMemory to get the variables - should
// still be pretty fast.
// Not implemented yet.
//#define RECORDER_USE_FAST_ACCESS

// Debugging only
//#define RECORDER_DONT_READ_VALUES
//#define RECORDER_DO_NOTHING

#include "recording_thread.h"

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
    void
    startRecording ();

    void
    stopRecording ();

    int
    getRowNumber ();

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

    //RecordingThread* m_thread; // not implemented currently - trying a process instead

    void readVariablesFile();
    void writeToFile();

    // recorded file variables
#ifdef USE_PROCESS
    FILE*           m_file_out;
#else
# ifdef USE_ZLIB_DIRECTLY
    void openZlibFile();
    void closeZlibFile();
    void writeSingleStringToFile(std::string& inp);

    FILE*           m_file_out;
    z_stream        m_zstrm;
# else
    ogzstream       m_file_out;
# endif
#endif

    std::string m_filename;
    bool m_file_init;           // true if m_fileout is open, false otherwise
    bool m_recording;           // are we recording
    int
        m_row;                  // which row of the csv file has been recorded

    AL::ALPtr < AL::ALBroker >      m_broker;        // needed for ConnectToVariables
    std::vector < std::string >     m_varnames;
    std::vector < float >           m_values;
    int                             m_values_size;
    AL::ALPtr < ALMemoryFastAccess > m_memoryfastaccess;

    //proxy to the logger module
    ALPtr < AL::ALLoggerProxy > m_log;

    //proxy to the memory module
    ALPtr < AL::ALMemoryProxy > m_memory;


};
#endif // recorder_H
