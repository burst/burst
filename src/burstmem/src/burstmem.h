/**
 * @author Eran Polosetski (NOT)
 * BURST 2009 - recorder module
 *
 */

#ifndef __BURSTMEM_H__
# define __BURSTMEM_H__

#include <vector>
#include <string>

#include <cstdio>

#include "alloggerproxy.h"
#include "almemoryproxy.h"
#include "alptr.h"
#include "almemoryfastaccess.h"

using namespace AL;

class burstmem:public
    AL::ALModule
{
  public:
    /**
     * Default Constructor.
     */
    burstmem (ALPtr < ALBroker > pBroker, std::string pName);

    /**
     * Destructor.
     */
    virtual ~
    burstmem ();

    // External module interface

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

    void dataChanged (const std::string & pDataName, const ALValue & pValue,
                 const std::string & pMessage) { }

  private:

    //RecordingThread* m_thread; // not implemented currently - trying a process instead

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
#endif // __BURSTMEM_H__

