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
#include "Kinematics.h"
#include "ALImageTranscriber.h"
#include "Vision.h"
#ifdef BURST_DO_LOCALIZATION_IN_MODULE
#include "LocSystem.h"
#include "BallEKF.h"
#endif //BURST_DO_LOCALIZATION_IN_MODULE

#include "burstutil.h"

#include "imopsmodule.h"
#include "imops.h"

using namespace AL;

using Kinematics::NUM_JOINTS;

////////////////////////////////////////////////////////////////////////////////
// Globals

// three acces, two gyros, two angles
#define NUM_INERTIAL_VARS 7

ALPtr<ImopsModule> g_limops;
volatile bool g_run_vision_thread = true;
pthread_t g_vision_thread;

////////////////////////////////////////////////////////////////////////////////

std::vector<std::string> createWriteList(); // forward declaration

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
    vision_frame_length_print_thresh_us(VISION_FRAME_LENGTH_PRINT_THRESH_uS),
    m_broker(pBroker)
{

    std::cout << "ImopsModule: Module starting" << std::endl;
    // Describe the module here
    setModuleDescription
        ("This is the imops module - does all the image processing (aka nao-man, but minus the rest)");

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

    // create a list of the variables we are interested in
    // - this is closely tied to the methods that get these
    char* vars[] = {
    "Device/SubDeviceList/HeadYaw/Position/Sensor/Value",
    "Device/SubDeviceList/HeadPitch/Position/Sensor/Value",

    "Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value",
    "Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value",
    "Device/SubDeviceList/LElbowYaw/Position/Sensor/Value",
    "Device/SubDeviceList/LElbowRoll/Position/Sensor/Value",
    "Device/SubDeviceList/LWristYaw/Position/Sensor/Value",
    "Device/SubDeviceList/LHand/Position/Sensor/Value",

    "Device/SubDeviceList/LHipYawPitch/Position/Sensor/Value",
    "Device/SubDeviceList/LHipRoll/Position/Sensor/Value",
    "Device/SubDeviceList/LHipPitch/Position/Sensor/Value",
    "Device/SubDeviceList/LKneePitch/Position/Sensor/Value",
    "Device/SubDeviceList/LAnklePitch/Position/Sensor/Value",
    "Device/SubDeviceList/LAnkleRoll/Position/Sensor/Value",

    // we don't get RHipYawPitch with fast since there *is* no such thing.
    // we shall try to use LHipYawPitch twice.
    "Device/SubDeviceList/LHipYawPitch/Position/Sensor/Value",
    "Device/SubDeviceList/RHipRoll/Position/Sensor/Value",
    "Device/SubDeviceList/RHipPitch/Position/Sensor/Value",
    "Device/SubDeviceList/RKneePitch/Position/Sensor/Value",
    "Device/SubDeviceList/RAnklePitch/Position/Sensor/Value",
    "Device/SubDeviceList/RAnkleRoll/Position/Sensor/Value",

    "Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value",
    "Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value",
    "Device/SubDeviceList/RElbowYaw/Position/Sensor/Value",
    "Device/SubDeviceList/RElbowRoll/Position/Sensor/Value",
    "Device/SubDeviceList/RWristYaw/Position/Sensor/Value",
    "Device/SubDeviceList/RHand/Position/Sensor/Value",

    "Device/SubDeviceList/InertialSensor/AccX/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AccY/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AccZ/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/GyrX/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/GyrY/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",
    "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",
    };
    m_varnames = std::vector<std::string>(vars, vars + sizeof(vars)/sizeof(char*));
    assert(m_varnames.size() == NUM_INERTIAL_VARS+NUM_JOINTS); // joints include hipyawpitch once.

    m_exported_vars = createWriteList(); // create list of exported variables
    m_exported.resize(m_exported_vars.size(), 0.0F);

    // create fast memory access proxy
    try {
        m_memoryfastaccess =
            AL::ALPtr<ALMemoryFastAccess >(new ALMemoryFastAccess());
        m_memoryfastaccess->ConnectToVariables(m_broker, m_varnames);
    } catch (AL::ALError e) {
        std::cout << "ImopsModule: Failed to create the ALFastMemoryAccess proxy: " <<
            e.toString() << std::endl;
    }

    // create second proxy for writing
    try {
        m_memoryfastwrite =
            AL::ALPtr<ALMemoryFastAccess >(new ALMemoryFastAccess());
        m_memoryfastwrite->ConnectToVariables(m_broker, m_exported_vars, true /* create if not already existing */);
    } catch (AL::ALError e) {
        std::cout << "ImopsModule: Failed to create the ALFastMemoryAccess proxy: " <<
            e.toString() << std::endl;
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
    g_imageTranscriber->setFrameRate(fps);
}

////////////////////////////////////////////////////////////////////////////////

// called from Vision Thread
void ImopsModule::notifyNextVisionImage() {
    // Synchronize noggin's information about joint angles with the motion
    // thread's information


    static FSR null_fsr(0.0F, 0.0F, 0.0F, 0.0F);
    // x, y, z, gyrx, gyry, anglex, angley
    
    static std::vector<float> values(NUM_JOINTS + NUM_INERTIAL_VARS, 0.0F);
    static std::vector<float> body_angles(NUM_JOINTS, 0.0F);
    try {
        m_memoryfastaccess->GetValues(values);
    } catch (AL::ALError e) {
        std::cout << "ImopsModule: m_memoryfastaccess->GetValues exception (using last values): " << e.toString() << std::endl;
    }
    // setBodyAngles just copies the vector, doesn't just take first NUM_JOINTS
    memcpy(&body_angles[0], &values[0], NUM_JOINTS*sizeof(float)); // TODO - time vs std::copy, prefer the later for safety

    g_sensors->setBodyAngles(body_angles);
    
    Inertial inertial(values[NUM_JOINTS], values[NUM_JOINTS+1],
        values[NUM_JOINTS+2], values[NUM_JOINTS+3],
        values[NUM_JOINTS+4], values[NUM_JOINTS+5], values[NUM_JOINTS+6]);

#ifdef WEBOTS
    inertial.angleX = inertial.angleY = 0.0F;
#endif

#ifdef DEBUG_IMAGE
    std::cout << "ImopsModule: angleX " << inertial.angleX
              << ", angleY " << inertial.angleY << " head_pitch " << body_angles[1] << std::endl;
#endif

    g_sensors->setMotionSensors(null_fsr, null_fsr, 0.0F /* ChestButton */, inertial, inertial);

    g_sensors->updateVisionAngles();

    // Process current frame
    g_vision->notifyImage(g_sensors->getImage());
    //Release the camera image
    //if(camera_active)
    g_imageTranscriber->releaseImage();

    static Counter writer("ImopsModule: Counter: time for writeToALMemory: ");
    writer.one();
    this->writeToALMemory();
    writer.two();

    // Make sure messages are printed
    fflush(stdout);
}

// <Burst>
// Export all variables to ALMemory for Burst integration (take 2)

// Define the list of variables used to export information from vision to behavior (player)
// code, or put otherwise from c++ to python code.
std::vector<std::string> createWriteList()
{ // 14
#define GOAL_POST_VARS(which, vision_var) \
    "/BURST/Vision/" which "/X", \
    "/BURST/Vision/" which "/Y", \
    "/BURST/Vision/" which "/CenterX", \
    "/BURST/Vision/" which "/CenterY", \
    "/BURST/Vision/" which "/AngleXDeg", \
    "/BURST/Vision/" which "/AngleYDeg", \
    "/BURST/Vision/" which "/Width", \
    "/BURST/Vision/" which "/Height", \
    "/BURST/Vision/" which "/FocDist", \
    "/BURST/Vision/" which "/Distance", \
    "/BURST/Vision/" which "/BearingDeg", \
    "/BURST/Vision/" which "/IDCertainty", \
    "/BURST/Vision/" which "/DistanceCertainty", \
    "/BURST/Vision/" which "/ElevationDeg", \
     
    
    char* vars[] = {
    "/BURST/Vision/Ball/CenterX",
    "/BURST/Vision/Ball/CenterY",
    "/BURST/Vision/Ball/Width",
    "/BURST/Vision/Ball/Height",
    "/BURST/Vision/Ball/FocDist",
    "/BURST/Vision/Ball/Distance",
    "/BURST/Vision/Ball/BearingDeg",
    "/BURST/Vision/Ball/ElevationDeg",
    "/BURST/Vision/Ball/Confidence", // 9

    "/BURST/Vision/YGCrossbar/X",
    "/BURST/Vision/YGCrossbar/Y",
    "/BURST/Vision/YGCrossbar/CenterX",
    "/BURST/Vision/YGCrossbar/CenterY",
    "/BURST/Vision/YGCrossbar/AngleXDeg",
    "/BURST/Vision/YGCrossbar/AngleYDeg",
    "/BURST/Vision/YGCrossbar/Width",
    "/BURST/Vision/YGCrossbar/Height",
    "/BURST/Vision/YGCrossbar/FocDist",
    "/BURST/Vision/YGCrossbar/Distance",
    "/BURST/Vision/YGCrossbar/BearingDeg",
    "/BURST/Vision/YGCrossbar/ElevationDeg",
    "/BURST/Vision/YGCrossbar/LeftOpening",
    "/BURST/Vision/YGCrossbar/RightOpening",
    "/BURST/Vision/YGCrossbar/shotAvailable", //15

    "/BURST/Vision/BGCrossbar/X",
    "/BURST/Vision/BGCrossbar/Y",
    "/BURST/Vision/BGCrossbar/CenterX",
    "/BURST/Vision/BGCrossbar/CenterY",
    "/BURST/Vision/BGCrossbar/AngleXDeg",
    "/BURST/Vision/BGCrossbar/AngleYDeg",
    "/BURST/Vision/BGCrossbar/Width",
    "/BURST/Vision/BGCrossbar/Height",
    "/BURST/Vision/BGCrossbar/FocDist",
    "/BURST/Vision/BGCrossbar/Distance",
    "/BURST/Vision/BGCrossbar/BearingDeg",
    "/BURST/Vision/BGCrossbar/ElevationDeg",
    "/BURST/Vision/BGCrossbar/LeftOpening",
    "/BURST/Vision/BGCrossbar/RightOpening",
    "/BURST/Vision/BGCrossbar/shotAvailable", //15

    // Blue Goal Right Post (BGRP)
    GOAL_POST_VARS("BGRP", bgrp)
    // Blue Goal Left Post (BGLP)
    GOAL_POST_VARS("BGLP", bglp)
    // Yellow Goal Right Post (YGRP)
    GOAL_POST_VARS("YGRP", ygrp)
    // Yellow Goal Left Post (YGRP)
    GOAL_POST_VARS("YGLP", yglp)
    }; // 95 total

#undef GOAL_POST_VARS

    int num_vars = sizeof(vars)/sizeof(char*);
    std::cout << "ImopsModule: will write " << num_vars << " variables" << std::endl;
    return std::vector<std::string>(vars, vars + num_vars);

#ifdef BURST_DO_LOCALIZATION_IN_MODULE
#error BURST_DO_LOCALIZATION_IN_MODULE is BROKEN
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

#define INSERT(obj, name, getter) \
    memory->insertData("/BURST/" base "/" obj "/" name, static_cast<float>(getter), 0)

    // Notice the parenthasis () on the getter in VISION

#define VISION(obj, name, getter) INSERT("Vision", obj, name, getter())
#define LOCALIZATION(obj, name, getter) INSERT("Loc", obj, name, getter)

    unsigned int i = 0;

    VisualBall* ball = g_vision->ball;
    m_exported[i++] = ball->getCenterX();
    m_exported[i++] = ball->getCenterY();
    m_exported[i++] = ball->getWidth();
    m_exported[i++] = ball->getHeight();
    m_exported[i++] = ball->getFocDist();
    m_exported[i++] = ball->getDistance();
    m_exported[i++] = ball->getBearingDeg();
    m_exported[i++] = ball->getElevationDeg();
    m_exported[i++] = ball->getConfidence();

    VisualCrossbar* crossbar = g_vision->ygCrossbar;

    m_exported[i++] = crossbar->getX();
    m_exported[i++] = crossbar->getY();
    m_exported[i++] = crossbar->getCenterX();
    m_exported[i++] = crossbar->getCenterY();
    m_exported[i++] = crossbar->getAngleXDeg();
    m_exported[i++] = crossbar->getAngleYDeg();
    m_exported[i++] = crossbar->getWidth();
    m_exported[i++] = crossbar->getHeight();
    m_exported[i++] = crossbar->getFocDist();
    m_exported[i++] = crossbar->getDistance();
    m_exported[i++] = crossbar->getBearingDeg();
    m_exported[i++] = crossbar->getElevationDeg();
    m_exported[i++] = crossbar->getLeftOpening();
    m_exported[i++] = crossbar->getRightOpening();
    m_exported[i++] = crossbar->shotAvailable();

    crossbar = g_vision->bgCrossbar;

    m_exported[i++] = crossbar->getX();
    m_exported[i++] = crossbar->getY();
    m_exported[i++] = crossbar->getCenterX();
    m_exported[i++] = crossbar->getCenterY();
    m_exported[i++] = crossbar->getAngleXDeg();
    m_exported[i++] = crossbar->getAngleYDeg();
    m_exported[i++] = crossbar->getWidth();
    m_exported[i++] = crossbar->getHeight();
    m_exported[i++] = crossbar->getFocDist();
    m_exported[i++] = crossbar->getDistance();
    m_exported[i++] = crossbar->getBearingDeg();
    m_exported[i++] = crossbar->getElevationDeg();
    m_exported[i++] = crossbar->getLeftOpening();
    m_exported[i++] = crossbar->getRightOpening();
    m_exported[i++] = crossbar->shotAvailable();

    // Blue Goal Right Post (BGRP)
    VisualFieldObject* post;
#define DO_GOAL_POST(which, vision_var) \
    post = g_vision->vision_var; \
    m_exported[i++] = post->getX(); \
    m_exported[i++] = post->getY(); \
    m_exported[i++] = post->getCenterX(); \
    m_exported[i++] = post->getCenterY(); \
    m_exported[i++] = post->getAngleXDeg(); \
    m_exported[i++] = post->getAngleYDeg(); \
    m_exported[i++] = post->getWidth(); \
    m_exported[i++] = post->getHeight(); \
    m_exported[i++] = post->getFocDist(); \
    m_exported[i++] = post->getDistance(); \
    m_exported[i++] = post->getBearingDeg(); \
    m_exported[i++] = post->getIDCertainty(); \
    m_exported[i++] = post->getDistanceCertainty(); \
    m_exported[i++] = post->getElevationDeg(); \

    DO_GOAL_POST("BGRP", bgrp)
    // Blue Goal Left Post (BGLP)
    DO_GOAL_POST("BGLP", bglp)
    // Yellow Goal Right Post (YGRP)
    DO_GOAL_POST("YGRP", ygrp)
    // Yellow Goal Left Post (YGRP)
    DO_GOAL_POST("YGLP", yglp)

#undef DO_GOAL_POST

    // fine, now actually write the values
    try {
        m_memoryfastwrite->SetValues(m_exported);
    } catch (AL::ALError e) {
        std::cout << "ImopsModule: m_memoryfastwrite->SetValues exception caught (values not updated!): "
                  << e.toString() << std::endl;
    }


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

