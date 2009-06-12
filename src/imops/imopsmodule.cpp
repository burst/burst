/**
 * \mainpage
 * \section Author
 * @author Alon Levy, heavily based on Northern Bites code
 *
 * \section Copyright
 * BURST team
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
#include <pthread.h>

#include <altypes.h>
#include <alxplatform.h>
#include <albrokermanager.h>
#include <alproxy.h>
#include <almemoryproxy.h>
#include <almotionproxy.h>

#include "Profiler.h"
#include "synchro.h"
#include "ALImageTranscriber.h"
#include "Vision.h"
#ifdef BURST_DO_LOCALIZATION_IN_MODULE
#include "LocSystem.h"
#include "BallEKF.h"
#endif //BURST_DO_LOCALIZATION_IN_MODULE

#include "imopsmodule.h"
#include "imops.h"

using namespace AL;

////////////////////////////////////////////////////////////////////////////////
// Globals

ALPtr<ImopsModule> g_limops;
volatile bool g_run_vision_thread = true;
pthread_t g_vision_thread;

////////////////////////////////////////////////////////////////////////////////

template<typename T>
    inline T t_max(T a, T b) {
        if (a > b) return a;
        return b;
    }

// This is the equivalent of the ALImageTranscriber, no mutexes involved.
// Not that I had any problem with that, only it stopped working for some
// reason.
void *getImageLoop(void *arg)
{
#ifdef BURST_DEBUG_VISION_THREAD
    int count = 0;
#endif
    while(g_run_vision_thread) {
        const useconds_t startTime = micro_time();
        g_imageTranscriber->waitForImage();
        g_limops->notifyNextVisionImage();
#ifdef BURST_DEBUG_VISION_THREAD
        std::cout << "image " << count++ << std::endl;
#endif
        const useconds_t processTime = micro_time() - startTime;
        volatile useconds_t vision_frame_length_us =
                        g_limops->vision_frame_length_us;
        volatile useconds_t vision_frame_length_print_thresh_us =
                        g_limops->vision_frame_length_print_thresh_us;
        if (processTime > vision_frame_length_us){
            if (processTime > vision_frame_length_print_thresh_us)
                cout << "Time spent in ALImageTranscriber loop longer than"
                     << " frame length: " << processTime <<endl;
            //Don't sleep at all
        } else{
            useconds_t sleepTime = vision_frame_length_us - processTime;
#ifdef BURST_DEBUG_VISION_THREAD
            std::cout << "sleeping for " << sleepTime << " us" << std::endl;
#endif
            usleep(static_cast<useconds_t>(sleepTime));
        }
    }
	return 0;
}

////////////////////////////////////////////////////////////////////////////////
// ImopsModule Constructor

ImopsModule::ImopsModule (ALPtr < ALBroker > pBroker, std::string pName)
    : ALModule (pBroker, pName),
    vision_frame_length_us(VISION_FRAME_LENGTH_uS),
    vision_frame_length_print_thresh_us(VISION_FRAME_LENGTH_PRINT_THRESH_uS)
{

    std::cout << "ImopsModule: Module starting" << std::endl;
    // Describe the module here
    setModuleDescription
        ("This is the imops module - does all the image processing");

    // Define callable methods with there description (left for easy copy/paste if required)
    functionName ("setFramesPerSecond", "imops", "change frames per second (doesn't change the grabs, just the processing)");
    BIND_METHOD (ImopsModule::setFramesPerSecond);

    //Create a proxy on memory module
    try {
        m_memory = getParentBroker()->getMemoryProxy();
    }
    catch (ALError & e) {
        std::
            cout << "could not create a proxy to ALMemory module" <<
            std::endl;
    }
    //Create a proxy on motion module
    try {
        m_motion = getParentBroker ()->getMotionProxy ();
    }
    catch (ALError & e) {
        std::
            cout << "could not create a proxy to ALMotion module" <<
            std::endl;
    }

    // init the vision parts (reads color table, does some allocs for threshold
    // data, object fragments)
    this->initVisionThread(pBroker);
    std::cout << "ImopsModule: Done creating vision thread" << std::endl;
}

void ImopsModule::setFramesPerSecond(double fps)
{
#ifdef BURST_DEBUG_VISION_THREAD
    std::cout << "ImopsModule: setFramesPerSecond: " << fps << std::endl;
#endif
    vision_frame_length_us = 1000000.0 / fps;
    vision_frame_length_print_thresh_us = vision_frame_length_us * 1.5; // TODO - set this to?
}

////////////////////////////////////////////////////////////////////////////////

void ImopsModule::notifyNextVisionImage() {
    // Synchronize noggin's information about joint angles with the motion
    // thread's information

    static char* inertial_vars_init[] = {
    "Device/SubDeviceList/InertialSensor/AccX/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AccY/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AccZ/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/GyrX/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/GyrY/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value"
    };
    static std::vector<std::string> inertial_vars = std::vector<std::string>(inertial_vars_init,
        inertial_vars_init + sizeof(inertial_vars_init)/sizeof(char*));

    static FSR null_fsr(0.0F, 0.0F, 0.0F, 0.0F);
    // x, y, z, gyrx, gyry, anglex, angley
    
    // this is brain dead now, but good for testing - Alon
    g_sensors->setBodyAngles(m_motion->getBodyAngles());
    
    std::vector<float> vals = m_memory->getListData(inertial_vars);
    Inertial inertial(vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6]);
#ifdef WEBOTS
    inertial.angleX = inertial.angleY = 0.0F;
#endif

#ifdef DEBUG_IMAGE
    std::cout << "ImopsModule: angleX " << inertial.angleX
              << ", angleY " << inertial.angleY << std::endl;
#endif

    g_sensors->setMotionSensors(null_fsr, null_fsr, 0.0F /* ChestButton */, inertial, inertial);

    g_sensors->updateVisionAngles();

    // Process current frame
    g_vision->notifyImage(g_sensors->getImage());

    this->writeToALMemory();

    //Release the camera image
    //if(camera_active)
    g_imageTranscriber->releaseImage();

    // Make sure messages are printed
    fflush(stdout);
}

// <Burst>
// Export all variables to ALMemory for Burst integration (take 2)

void ImopsModule::writeToALMemory()
{
    static bool memory_initialized = false;
    static AL::ALPtr<AL::ALMemoryProxy> memory;

    if (!memory_initialized) {
        AL::ALPtr<AL::ALBrokerManager> brokermanager = AL::ALBrokerManager::getInstance();
        AL::ALPtr<AL::ALBroker> broker = brokermanager->getAnyBroker();
        AL::ALPtr<AL::ALMemoryProxy> temp_memory(new AL::ALMemoryProxy(broker));
        memory = temp_memory;
        memory_initialized = true;
    }

    // TODO MAJOR: use insertListData

    // BALL
    // from PyBall_update
    // XXX MAJOR UGLINESS
    // converting everything to float to:
    // avoid having to use multiple different arrays when reading all of this
    // with anything (such as ALMemory->getListData or ALMemoryFastAccess)
    //
    // results in: waste of memory
    // ugly code
    // possible ambiguous values? int->float can lose data? no, unless really large.
    // bool->float? neither (just wasted cycles, not really a problem)

#define INSERT(base, obj, name, getter) \
    memory->insertData("/BURST/" base "/" obj "/" name, static_cast<float>(getter), 0)

    // Notice the parenthasis () on the getter in VISION

#define VISION(obj, name, getter) INSERT("Vision", obj, name, getter())
#define LOCALIZATION(obj, name, getter) INSERT("Loc", obj, name, getter)

    VisualBall* ball = g_vision->ball;
    VISION("Ball", "CenterX", ball->getCenterX);
    VISION("Ball", "CenterY", ball->getCenterY);
    VISION("Ball", "Width", ball->getWidth);
    VISION("Ball", "Height", ball->getHeight);
    VISION("Ball", "FocDist", ball->getFocDist);
    VISION("Ball", "Distance", ball->getDistance);
    VISION("Ball", "BearingDeg", ball->getBearingDeg);
    VISION("Ball", "ElevationDeg", ball->getElevationDeg);
    VISION("Ball", "Confidence", ball->getConfidence);

    VisualCrossbar* crossbar = g_vision->ygCrossbar;

    VISION("YGCrossbar", "X", crossbar->getX);
    VISION("YGCrossbar", "Y", crossbar->getY);
    VISION("YGCrossbar", "CenterX", crossbar->getCenterX);
    VISION("YGCrossbar", "CenterY", crossbar->getCenterY);
    VISION("YGCrossbar", "AngleXDeg", crossbar->getAngleXDeg);
    VISION("YGCrossbar", "AngleYDeg", crossbar->getAngleYDeg);
    VISION("YGCrossbar", "Width", crossbar->getWidth);
    VISION("YGCrossbar", "Height", crossbar->getHeight);
    VISION("YGCrossbar", "FocDist", crossbar->getFocDist);
    VISION("YGCrossbar", "Distance", crossbar->getDistance);
    VISION("YGCrossbar", "BearingDeg", crossbar->getBearingDeg);
    VISION("YGCrossbar", "ElevationDeg", crossbar->getElevationDeg);
    VISION("YGCrossbar", "LeftOpening", crossbar->getLeftOpening);
    VISION("YGCrossbar", "RightOpening", crossbar->getRightOpening);
    VISION("YGCrossbar", "shotAvailable", crossbar->shotAvailable);

    crossbar = g_vision->bgCrossbar;

    VISION("BGCrossbar", "X", crossbar->getX);
    VISION("BGCrossbar", "Y", crossbar->getY);
    VISION("BGCrossbar", "CenterX", crossbar->getCenterX);
    VISION("BGCrossbar", "CenterY", crossbar->getCenterY);
    VISION("BGCrossbar", "AngleXDeg", crossbar->getAngleXDeg);
    VISION("BGCrossbar", "AngleYDeg", crossbar->getAngleYDeg);
    VISION("BGCrossbar", "Width", crossbar->getWidth);
    VISION("BGCrossbar", "Height", crossbar->getHeight);
    VISION("BGCrossbar", "FocDist", crossbar->getFocDist);
    VISION("BGCrossbar", "Distance", crossbar->getDistance);
    VISION("BGCrossbar", "BearingDeg", crossbar->getBearingDeg);
    VISION("BGCrossbar", "ElevationDeg", crossbar->getElevationDeg);
    VISION("BGCrossbar", "LeftOpening", crossbar->getLeftOpening);
    VISION("BGCrossbar", "RightOpening", crossbar->getRightOpening);
    VISION("BGCrossbar", "shotAvailable", crossbar->shotAvailable);

    // Blue Goal Right Post (BGRP)
    VisualFieldObject* post;
#define DO_GOAL_POST(which, vision_var) \
    post = g_vision->vision_var; \
    VISION(which, "X", post->getX); \
    VISION(which, "Y", post->getY); \
    VISION(which, "CenterX", post->getCenterX); \
    VISION(which, "CenterY", post->getCenterY); \
    VISION(which, "AngleXDeg", post->getAngleXDeg); \
    VISION(which, "AngleYDeg", post->getAngleYDeg); \
    VISION(which, "Width", post->getWidth); \
    VISION(which, "Height", post->getHeight); \
    VISION(which, "FocDist", post->getFocDist); \
    VISION(which, "Distance", post->getDistance); \
    VISION(which, "BearingDeg", post->getBearingDeg); \
    VISION(which, "IDCertainty", post->getIDCertainty); \
    VISION(which, "DistanceCertainty", post->getDistanceCertainty); \
    VISION(which, "ElevationDeg", post->getElevationDeg); \

    DO_GOAL_POST("BGRP", bgrp)
    // Blue Goal Left Post (BGLP)
    DO_GOAL_POST("BGLP", bglp)
    // Yellow Goal Right Post (YGRP)
    DO_GOAL_POST("YGRP", ygrp)
    // Yellow Goal Left Post (YGRP)
    DO_GOAL_POST("YGLP", yglp)

#ifdef BURST_DO_LOCALIZATION_IN_MODULE
    boost::shared_ptr<LocSystem> loc(noggin->loc);
    boost::shared_ptr<BallEKF> ballEKF(noggin->ballEKF); // access to localization data

    // Localization data
    LOCALIZATION("Self", "XEst", loc->getXEst());
    LOCALIZATION("Self", "YEst", loc->getYEst());
    LOCALIZATION("Self", "HEstDeg", loc->getHEstDeg());
    LOCALIZATION("Self", "HEst", loc->getHEst());
    LOCALIZATION("Self", "XUncert", loc->getXUncert());
    LOCALIZATION("Self", "YUncert", loc->getYUncert());
    LOCALIZATION("Self", "HUncertDeg", loc->getHUncertDeg());
    LOCALIZATION("Self", "HUncert", loc->getHUncert());
    LOCALIZATION("Self", "LastOdoDeltaF", loc->getLastOdo().deltaF);
    LOCALIZATION("Self", "LastOdoDeltaL", loc->getLastOdo().deltaL);
    LOCALIZATION("Self", "LastOdoDeltaR", loc->getLastOdo().deltaR);

    LOCALIZATION("Ball", "XEst", ballEKF->getXEst());
    LOCALIZATION("Ball", "YEst", ballEKF->getYEst());
    LOCALIZATION("Ball", "XVelocityEst", ballEKF->getXVelocityEst());
    LOCALIZATION("Ball", "YVelocityEst", ballEKF->getYVelocityEst());
    LOCALIZATION("Ball", "XUncert", ballEKF->getXUncert());
    LOCALIZATION("Ball", "YUncert", ballEKF->getYUncert());
    LOCALIZATION("Ball", "XVelocityUncert", ballEKF->getXVelocityUncert());
    LOCALIZATION("Ball", "YVelocityUncert", ballEKF->getYVelocityUncert());
#endif // BURST_DO_LOCALIZATION_IN_MODULE
}
// </Burst>


void ImopsModule::initVisionThread( ALPtr<ALBroker> broker )
{
    // Now create the thread that will a) get new images and b) process them
    // This is basically the same as nao-man/manmodule.cpp (northernbites) but
    // we skip the ALTranscriber that isn't required, ending up with a single
    // thread. (I hope - to be checked. Maybe this thread stays there too?
    // or I hope it's just a function call from a naoqi thread that was already
    // there)
    init_vision(); // creates everything except the threading stuff and the proxy stuff.
    #if 0
    {
        // stops after about 30 frames, no idea why.
        g_synchro = boost::shared_ptr<Synchro>(new Synchro());
        g_imageTranscriber =
            boost::shared_ptr<ALImageTranscriber>
            (new ALImageTranscriber(g_synchro, g_sensors, broker));
        g_imageTranscriber->setSubscriber(this);
        g_imageTranscriber->start();
    }
    #else
    {
        g_synchro = boost::shared_ptr<Synchro>(new Synchro());
        g_imageTranscriber =
            boost::shared_ptr<ALImageTranscriber>
            (new ALImageTranscriber(g_synchro, g_sensors, broker));
        g_imageTranscriber->setSubscriber(this);

#ifdef BURST_DEBUG_VISION_THREAD
        std::cout << "ImopsModule, getImageLoop: " << vision_frame_length_us
            << ", " << vision_frame_length_print_thresh_us << std::endl;
#endif

        pthread_create(&g_vision_thread, NULL, getImageLoop, NULL);
    }
    #endif
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
    std::cout << "ImopsModule:: being deleted" << std::endl;
    g_imageTranscriber->stop();
}

////////////////////////////////////////////////////////////////////////////////

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
    g_limops = ALModule::createModule<ImopsModule>(pBroker, "imops");

    return 0;
  }

  int _closeModule ()
  {
    // Delete module instance
    // ALPtr - reference counted, right?
    //delete g_limops;
    g_run_vision_thread = false;
    pthread_join(g_vision_thread, NULL);
    std::cout << "ImopsModule: joined vision thread" << std::endl;

    return 0;
  }

# ifdef __cplusplus
}
# endif

