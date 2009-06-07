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

class ImopsModule : public AL::ALModule, public ImageSubscriber
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

  private:

    // Battery checking functionality

    void initVisionThread( ALPtr<ALBroker> broker );

    AL::ALPtr < AL::ALBroker >      m_broker;        // needed for ConnectToVariables
    AL::ALPtr < ALMemoryFastAccess > m_memoryfastaccess;

    //proxy to the memory module
    ALPtr < AL::ALMemoryProxy > m_memory;

    void writeToALMemory();
    void notifyNextVisionImage();
    void processFrame();
};

#endif // IMOPS_H
