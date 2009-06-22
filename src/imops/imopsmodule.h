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

    void setFramesPerSecond(const double &fps);
    void switchToTopCamera();
    void switchToBottomCamera();

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

    virtual std::string httpGet() const {
        return "Image Processing module - nao-man slim version";
    }

    // public interface for thread that calls us

    void notifyNextVisionImage();

    // used by the getImageLoop

    useconds_t                      vision_frame_length_us;
    useconds_t                      vision_frame_length_print_thresh_us;

    volatile bool                   m_switchRequested;
    volatile bool                   m_requestedTopCamera;

    // needs to be called after the instance is created, since we use a global (err, TODO)
    void initVisionThread( ALPtr<ALBroker> broker );

  private:

    std::vector<std::string>         m_varnames; // all float variables vision needs
    std::vector<std::string>         m_exported_vars; // variables exported to ALMemory for player.py
    std::vector<float>               m_exported; // float values to be exported.

    AL::ALPtr < AL::ALBroker >       m_broker;        // needed for ConnectToVariables
    AL::ALPtr < ALMemoryFastAccess > m_memoryfastaccess;
    AL::ALPtr < ALMemoryFastAccess > m_memoryfastwrite;

    ALPtr < AL::ALMemoryProxy >      m_memory;
    ALPtr < AL::ALMotionProxy >      m_motion;

    void writeToALMemory();
};

#endif // IMOPS_H
