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

    void        startMemoryMap();
    void        stopMemoryMap();
    bool        isMemoryMapRunning();

    void        clearMappedVariables();
    void        addMappedVariable(int index, std::string var);

    // TODO - get the fucking std::vector<std::string> wrapping to work
    //void        setMappedVariables(const std::vector<std::string>);
    int         getNumberOfVariables();
    std::string getVarNameByIndex(int i);
    
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
                 const std::string & pMessage);

  private:

    // Battery checking functionality

    static const int CHARGER_UNKNOWN, CHARGER_CONNECTED, CHARGER_DISCONNECTED;
    int numberOfTicksBeforeAnnouncement;
    int ticksLastStatusHasHeld;
    int lastBatteryStatus;
    void readBatteryChargerWarningConfig();
    
    void checkBatteryStatus();

    void announceChargerChange( int status );

    void subscribeToDataChange();

    void updateMemoryMappedVariables();

    bool                            m_copying;
    bool                            m_memory_mapped;

    int                             m_mmap_fd;

    AL::ALPtr < AL::ALBroker >      m_broker;        // needed for ConnectToVariables
    std::vector < std::string >     m_varnames;
    std::vector < float >           m_values;       // TODO - use a smart pointer. need to get me one of those.
    float*                          m_mmap;         // memory mapped pointer
    AL::ALPtr < ALMemoryFastAccess > m_memoryfastaccess;

    //proxy to the logger module
    ALPtr < AL::ALLoggerProxy > m_log;

    //proxy to the memory module
    ALPtr < AL::ALMemoryProxy > m_memory;

    // Proxy to the TextToSpeech module
    ALPtr < AL::ALProxy > textToSpeechProxy;

};
#endif // __BURSTMEM_H__

