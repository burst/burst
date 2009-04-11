/**
 * @author Eran Polosetski
 * BURST 2009 - Vision module
 *
 */

#ifndef vision_H
# define vision_H
# include "visionmodule.h"
#include "alloggerproxy.h"
#include "almemoryproxy.h"
#include "alptr.h"
#include "opencv/cv.h"
using namespace AL;

class vision : public AL::ALModule {
  public:
    /**
     * Default Constructor.
     */
    vision( ALPtr<ALBroker> pBroker, std::string pName );

    /**
     * Destructor.
     */
     virtual ~vision();

    /**
     * registerToVIM : Register to the V.I.M.
     */
    void registerToVIM();

    /**
     * unRegisterFromVIM : Unregister from the V.I.M.
     */
    void unRegisterFromVIM();

    /**
     * setCamera : select the current camera.
     * @param whichCam index of the camera (0 - top, 1 - bottom)
     */
    void setCamera(int whichCam);

    /**
     * saveImage : save the last image received.
     * @param pName path of the file
     */
    void saveImage(std::string pName);

    /**
     * saveImageRaw : save the last image received (raw).
     */
    void saveImageRaw();

    /**
     * saveImageRemote : save the last image received. To be used if visionmodule is a remote module.
     * @param pName path of the file
     */
    void saveImageRemote(std::string pName);

    /**
     * testRemote : test remote image
     */
    void testRemote();

    /**
     * getBallRemote : Get the ball rect (within the field area!). To be used if the visionmodule is a remote module.
     * @return an ALValue\n
     */
    ALValue getBallRemote();

    /**
     * getBall : Get the ball rect (within the field area!). To be used if the visionmodule is a local module.
     * @return an ALValue\n
     */
    ALValue getBall();

    /**
     * version
     * @return The version number of ALLeds
     */
    std::string version();


    /**
     * innerTest
     * @return True if all the tests passed
     */
    bool innerTest(){ return true;};

    // **************************** BOUND METHODS **********************************
    /* dataChanged. Called by stm when subcription
     * has been modified.
     * @param pDataName Name of the suscribed data
     * @param pValue Value of the suscribed data
     * @param pMessage Message written by user during subscription
     */
    void dataChanged(const std::string& pDataName, const ALValue& pValue, const std::string& pMessage);

    void start(void);
    void stop(void);

  private :
    //proxy to the logger module
    ALPtr<AL::ALLoggerProxy> log;

    //proxy to the memory module
    ALPtr<AL::ALMemoryProxy> memory;

    //proxy on the video input module
    ALPtr<AL::ALProxy> camera;

    //name for the G.V.M.
    string name;

    //the resolution among : kVGA ( 640 * 480 ), kQVGA ( 320 * 240 ), kQQVGA ( 160 * 120 ).
    // ( definitions included in alvisiondefinitions.h )
    int resolution;

    //color space among : kYuvColorSpace, kyUvColorSpace, kyuVColorSpace,
    //       kYUVColorSpace, kYUV422InterlacedColorSpace, kRGBColorSpace.
    //  ( definitions contained in alvisiondefinitions.h )
    int colorSpace;

    CvSeq* getLargestColoredContour(IplImage* src, int iBoxColorValue, int iBoxColorRange, int iBoxSaturationCutoff, int iMinimalArea, CvRect &rect);
    //CvSeq* getHullByColor(IplImage* img, int iBoxColorValue, int iBoxColorRange, int iBoxSaturationCutoff, int iMinimalArea);

    CvMemStorage* storage;

    // Camera identification
    static const int TOP_CAMERA = 0;
    static const int BOTTOM_CAMERA = 1;

    // Camera setup information
    static const int CAMERA_SLEEP_TIME = 200;

};
#endif // vision_H
