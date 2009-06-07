/**
 * @author Also not Eran
 * Bar Ilan Maverick Robotics Lab.
 *
 */

#ifndef IMOPS_H
# define IMOPS_H

// ..::: Headers ::
#include <vector>
#include <string>

#include <cstdio>
# include <fstream>
# include <sstream>

# include "alxplatform.h"
//# include "config.h"

# include <albroker.h>
# include <almodule.h>
# include <altools.h>
#include <alloggerproxy.h>
#include <almemoryproxy.h>
#include <alptr.h>
#include <almemoryfastaccess.h>

using namespace AL;

class ImopsModule:public
    AL::ALModule
{
  public:
    /**
     * Default Constructor.
     */
    ImopsModule (ALPtr < ALBroker > pBroker, std::string pName);

    /**
     * Destructor.
     */
    virtual ~
    ImopsModule ();

    // External module interface

    // NONE - we just update ALMemory vars directly.

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

    // callback - signal to do all of our work (TODO: make this 15hz or whatever
    // - or just create a different thread for us? yeah, probably right.
    // OR, mmap the whole frame, whooping 150KiB of it!)
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

    AL::ALPtr < AL::ALBroker >      m_broker;        // needed for ConnectToVariables
    AL::ALPtr < ALMemoryFastAccess > m_memoryfastaccess;

    //proxy to the memory module
    ALPtr < AL::ALMemoryProxy > m_memory;

};

#endif // IMOPS_H
