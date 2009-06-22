// alvalue.h uses printf, but doesn't do the include, g++ 4.4.0 complains
#include <cstdio>

#include "alimage.h"
#include "alvisiondefinitions.h"

#include "manconfig.h"

#include "ALImageTranscriber.h"

using boost::shared_ptr;
using namespace AL;

const int ALImageTranscriber::DEFAULT_CAMERA_HUE;
const int ALImageTranscriber::DEFAULT_CAMERA_GAIN;
const int ALImageTranscriber::DEFAULT_CAMERA_LENSX;
const int ALImageTranscriber::DEFAULT_CAMERA_LENSY;
const int ALImageTranscriber::DEFAULT_CAMERA_CONTRAST;
const int ALImageTranscriber::DEFAULT_CAMERA_EXPOSURE;
const int ALImageTranscriber::DEFAULT_CAMERA_AUTO_GAIN;
const int ALImageTranscriber::DEFAULT_CAMERA_REDCHROMA;
const int ALImageTranscriber::DEFAULT_CAMERA_BLUECHROMA;
const int ALImageTranscriber::DEFAULT_CAMERA_BRIGHTNESS;
const int ALImageTranscriber::DEFAULT_CAMERA_SATURATION;
const int ALImageTranscriber::DEFAULT_CAMERA_AUTO_EXPOSITION;
const int ALImageTranscriber::DEFAULT_CAMERA_AUTO_WHITEBALANCE;

ALImageTranscriber::ALImageTranscriber(shared_ptr<Synchro> synchro,
                                       shared_ptr<Sensors> s,
                                       ALPtr<ALBroker> broker)
    : ThreadedImageTranscriber(s,synchro,"ALImageTranscriber"),
      log(), camera(), lem_name(""), camera_active(false),
      image(new unsigned char[IMAGE_BYTE_SIZE])
{
    try {
        log = broker->getLoggerProxy();
        // Possible values are
        // lowDebug, debug, lowInfo, info, warning, error, fatal
        log->setVerbosity("lowDebug");
    }catch (ALError &e) {
        std::cerr << "Could not create a proxy to ALLogger module" << std::endl;
    }

    subscribeCamera(broker);
    if(camera_active) {
        try{
            initCameraSettings(BOTTOM_CAMERA);
        }catch(ALError &e){
            cout << "Failed to init the camera settings:"<<e.toString()<<endl;
            camera_active = false;
        }
    }
    else
        cout << "\tCamera is inactive!" << endl;
}

ALImageTranscriber::~ALImageTranscriber() {
    delete [] image;
    stop();
}


int ALImageTranscriber::start() {
    return Thread::start();
}

void ALImageTranscriber::run() {
    Thread::running = true;
    Thread::trigger->on();

	long long lastProcessTimeAvg = VISION_FRAME_LENGTH_uS;
    while (Thread::running) {

        //start timer
        const long long startTime = micro_time();
        if (camera_active)
            waitForImage();

        subscriber->notifyNextVisionImage();

        //stop timer
        const long long processTime = micro_time() - startTime;
        //sleep until next frame

		lastProcessTimeAvg = lastProcessTimeAvg/2 + processTime/2;
        if (lastProcessTimeAvg > VISION_FRAME_LENGTH_uS){
			if (lastProcessTimeAvg > VISION_FRAME_LENGTH_PRINT_THRESH_uS)
				cout << "Time spent in ALImageTranscriber loop longer than"
					 << " frame length: " << processTime <<endl;
            //Don't sleep at all
        } else{
            // cout << "Sleeping for " << VISION_FRAME_LENGTH_uS
            //    -processTime << endl;

            //usleep(10000000);
            usleep(static_cast<useconds_t>(VISION_FRAME_LENGTH_uS
                                           -processTime));
        }
    }

    Thread::trigger->off();
}

void ALImageTranscriber::stop() {
    cout << "Stopping ALImageTranscriber" << endl;
    running = false;
    if(camera_active){
        cout << "lem_name = " << lem_name << endl;
        try {
            camera->callVoid("unsubscribe", lem_name);
        }catch (ALError &e) {
            log->error("Man", "Could not call the unsubscribe method of the ALVideoDevice "
                       "module");
        }
    }

    Thread::stop();
}

void ALImageTranscriber::subscribeCamera(ALPtr<ALBroker> broker) {
    try {
        camera = broker->getProxy("ALVideoDevice");
        camera_active =true;
    }catch (ALError &e) {
        log->error("ALImageTranscriber",
                   "Could not create a proxy to ALVideoDevice module");
        camera_active =false;
        return;
    }

    lem_name = "ALImageTranscriber_LEM";
    int format = NAO_IMAGE_SIZE;
    int colorSpace = NAO_COLOR_SPACE;
    int fps = DEFAULT_CAMERA_FRAMERATE;

    int resolution = format;



#ifdef DEBUG_MAN_INITIALIZATION
    printf("  Registering LEM with format=%i colorSpace=%i fps=%i\n", format,
           colorSpace, fps);
#endif

    try {
        lem_name = camera->call<std::string>("subscribe", lem_name, format,
                                             colorSpace, fps);
        cout << "Registered Camera: " << lem_name << " successfully"<<endl;
    } catch (ALError &e) {
        cout << "Failed to subscribe camera" << lem_name << endl;
        camera_active = false;
//         SleepMs(500);

//         try {
//             printf("LEM failed once, trying again\n");
//             lem_name = camera->call<std::string>("subscribe", lem_name, format,
//                                                  colorSpace, fps);
//         }catch (ALError &e2) {
//             log->error("ALImageTranscriber", "Could not call the subscribe method of the ALVideoDevice "
//                        "module\n" + e2.toString());
//             return;
//         }
    }

}

// set frame rate to the smallest number within the allowed values that
// is bigger or equal to given fps.
bool ALImageTranscriber::setFrameRate(unsigned int fps) {
    static unsigned int allowed_fps[] = {5, 10, 15, 30}; // see ALVideoDevice module setFrameRate help
    const unsigned int num_allowed = sizeof(allowed_fps) / sizeof(int);
    unsigned int i = 0;
    for (; allowed_fps[i] < fps && i < num_allowed ; ++i) {};
    if (i >= num_allowed) i = num_allowed - 1;
    std::cout << "ImopsModule: ALImageTranscriber: setFrameRate: given " << fps
              << ", set to " << allowed_fps[i] << std::endl;
    return camera->call<bool>( "setFrameRate", lem_name, static_cast<int>(allowed_fps[i])); // AL is brain dead about unsigned stuff.
}

void ALImageTranscriber::initCameraSettings(int whichCam){

    int currentCam =  camera->call<int>( "getParam", kCameraSelectID );
    if (whichCam != currentCam){
        camera->callVoid( "setParam", kCameraSelectID,whichCam);
        SleepMs(CAMERA_SLEEP_TIME);
        currentCam =  camera->call<int>( "getParam", kCameraSelectID );
        if (whichCam != currentCam){
            cout << "Failed to switch to camera "<<whichCam
                 <<" retry in " << CAMERA_SLEEP_TIME <<" ms" <<endl;
            SleepMs(CAMERA_SLEEP_TIME);
            currentCam =  camera->call<int>( "getParam", kCameraSelectID );
            if (whichCam != currentCam){
                cout << "Failed to switch to camera "<<whichCam
                     <<" ... returning, no parameters initialized" <<endl;
                return;
            }
        }
        cout << "Switched to camera " << whichCam <<" successfully"<<endl;
    }

    // Turn off auto settings
    // Auto exposure
    try {
        camera->callVoid("setParam", kCameraAutoExpositionID,
                         DEFAULT_CAMERA_AUTO_EXPOSITION);
    } catch (ALError &e){
        log->error("ALImageTranscriber", "Couldn't set AutoExposition");
    }
    int param = 0;
#define SAFE_GET_PARAM(which, defaultval) \
        param = defaultval; \
        try { \
            param = camera->call<int>("getParam", which); \
        } catch (ALError &e) { \
            log->error("ALImageTranscriber", "Couldn't get " # which); \
        }

    SAFE_GET_PARAM(kCameraAutoExpositionID, DEFAULT_CAMERA_AUTO_EXPOSITION);
	// if that didn't work, then try again
	if (param != DEFAULT_CAMERA_AUTO_EXPOSITION) {
		try {
			camera->callVoid("setParam", kCameraAutoExpositionID,
							 DEFAULT_CAMERA_AUTO_EXPOSITION);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set AutoExposition AGAIN");
		}
	}
    // Auto white balance
    try {
        camera->callVoid("setParam", kCameraAutoWhiteBalanceID,
                         DEFAULT_CAMERA_AUTO_WHITEBALANCE);

    } catch (ALError &e){
        log->error("ALImageTranscriber", "Couldn't set AutoWhiteBalance");
    }
    SAFE_GET_PARAM(kCameraAutoWhiteBalanceID, DEFAULT_CAMERA_AUTO_WHITEBALANCE);
	if (param != DEFAULT_CAMERA_AUTO_WHITEBALANCE) {
		try {
			camera->callVoid("setParam", kCameraAutoWhiteBalanceID,
							 DEFAULT_CAMERA_AUTO_WHITEBALANCE);
		} catch (ALError &e){
			log->error("ALImageTranscriber","Couldn't set AutoWhiteBalance AGAIN");
		}
	}
    // Auto gain
    try {
        camera->callVoid("setParam", kCameraAutoGainID,
                         DEFAULT_CAMERA_AUTO_GAIN);
    } catch (ALError &e){
        log->error("ALImageTranscriber", "Couldn't set AutoGain");
    }
	SAFE_GET_PARAM(kCameraAutoGainID, DEFAULT_CAMERA_AUTO_GAIN);
	if (param != DEFAULT_CAMERA_AUTO_GAIN) {
		try {
			camera->callVoid("setParam", kCameraAutoGainID,
							 DEFAULT_CAMERA_AUTO_GAIN);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set AutoGain AGAIN");
		}
	}
    // Set camera defaults
    // brightness
    try {
        camera->callVoid("setParam", kCameraBrightnessID,
                         DEFAULT_CAMERA_BRIGHTNESS);
    } catch (ALError &e){
        log->error("ALImageTranscriber", "Couldn't set Brightness ");
    }
	SAFE_GET_PARAM(kCameraBrightnessID, DEFAULT_CAMERA_BRIGHTNESS);
	if (param != DEFAULT_CAMERA_BRIGHTNESS) {
		try {
			camera->callVoid("setParam", kCameraBrightnessID,
							 DEFAULT_CAMERA_BRIGHTNESS);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set BRIGHTNESS AGAIN");
		}
	}
    // contrast
    try {
        camera->callVoid("setParam", kCameraContrastID,
                         DEFAULT_CAMERA_CONTRAST);
    } catch (ALError &e){
        log->error("ALImageTranscriber", "Couldn't set Contrast");
    }
	SAFE_GET_PARAM(kCameraContrastID, DEFAULT_CAMERA_CONTRAST);
	if (param != DEFAULT_CAMERA_CONTRAST) {
		try {
			camera->callVoid("setParam", kCameraContrastID,
							 DEFAULT_CAMERA_CONTRAST);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set Contrast AGAIN");
		}
	}
    // Red chroma
    try {
        camera->callVoid("setParam", kCameraRedChromaID,
                         DEFAULT_CAMERA_REDCHROMA);
    } catch (ALError &e){
        log->error("ALImageTranscriber", "Couldn't set RedChroma");
    }
	SAFE_GET_PARAM(kCameraRedChromaID, DEFAULT_CAMERA_REDCHROMA);
	if (param != DEFAULT_CAMERA_REDCHROMA) {
		try {
			camera->callVoid("setParam", kCameraRedChromaID,
							 DEFAULT_CAMERA_REDCHROMA);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set RedChroma AGAIN");
		}
	}
    // Blue chroma
    try {
        camera->callVoid("setParam", kCameraBlueChromaID,
                         DEFAULT_CAMERA_BLUECHROMA);
    } catch (ALError &e){
        log->error("ALImageTranscriber", "Couldn't set BlueChroma");
    }
	SAFE_GET_PARAM(kCameraBlueChromaID, DEFAULT_CAMERA_BLUECHROMA);
	if (param != DEFAULT_CAMERA_BLUECHROMA) {
		try {
			camera->callVoid("setParam", kCameraBlueChromaID,
							 DEFAULT_CAMERA_BLUECHROMA);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set BlueChroma AGAIN");
		}
	}
    // Exposure length
    try {
        camera->callVoid("setParam",kCameraExposureID,
                         DEFAULT_CAMERA_EXPOSURE);
    } catch (ALError &e) {
        log->error("ALImageTranscriber", "Couldn't set Exposure");
    }
	SAFE_GET_PARAM(kCameraExposureID, DEFAULT_CAMERA_EXPOSURE);
	if (param != DEFAULT_CAMERA_EXPOSURE) {
		try {
			camera->callVoid("setParam", kCameraExposureID,
							 DEFAULT_CAMERA_EXPOSURE);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set Exposure AGAIN");
		}
	}
    // Gain
    try {
        camera->callVoid("setParam",kCameraGainID,
                         DEFAULT_CAMERA_GAIN);
    } catch (ALError &e) {
        log->error("ALImageTranscriber", "Couldn't set Gain");
    }
	SAFE_GET_PARAM(kCameraGainID, DEFAULT_CAMERA_GAIN);
	if (param != DEFAULT_CAMERA_GAIN) {
		try {
			camera->callVoid("setParam", kCameraGainID,
							 DEFAULT_CAMERA_GAIN);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set Gain AGAIN");
		}
	}
    // Saturation
    try {
        camera->callVoid("setParam",kCameraSaturationID,
                         DEFAULT_CAMERA_SATURATION);
    } catch (ALError &e) {
        log->error("ALImageTranscriber", "Couldn't set Saturation");
    }
	SAFE_GET_PARAM(kCameraSaturationID, DEFAULT_CAMERA_SATURATION);
	if (param != DEFAULT_CAMERA_SATURATION) {
		try {
			camera->callVoid("setParam", kCameraSaturationID,
							 DEFAULT_CAMERA_SATURATION);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set Saturation AGAIN");
		}
	}
    // Hue
    try {
        camera->callVoid("setParam",kCameraHueID,
                         DEFAULT_CAMERA_HUE);
    } catch (ALError &e) {
        log->error("ALImageTranscriber", "Couldn't set Hue");
    }
	SAFE_GET_PARAM(kCameraHueID, DEFAULT_CAMERA_HUE);
	if (param != DEFAULT_CAMERA_HUE) {
		try {
			camera->callVoid("setParam", kCameraHueID,
							 DEFAULT_CAMERA_HUE);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set Hue AGAIN");
		}
	}
    // Lens correction X
    try {
        camera->callVoid("setParam",kCameraLensXID,
                         DEFAULT_CAMERA_LENSX);
    } catch (ALError &e) {
        log->error("ALImageTranscriber", "Couldn't set Lens Correction X");
    }
	SAFE_GET_PARAM(kCameraLensXID, DEFAULT_CAMERA_LENSX);
	if (param != DEFAULT_CAMERA_LENSX) {
		try {
			camera->callVoid("setParam", kCameraLensXID,
							 DEFAULT_CAMERA_LENSX);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set Lens Correction X AGAIN");
		}
	}
    // Lens correction Y
    try {
        camera->callVoid("setParam",kCameraLensYID,
                         DEFAULT_CAMERA_LENSY);
    } catch (ALError &e) {
        log->error("ALImageTranscriber", "Couldn't set Lens Correction Y");
    }
	SAFE_GET_PARAM(kCameraLensYID, DEFAULT_CAMERA_LENSY);
	if (param != DEFAULT_CAMERA_LENSY) {
		try {
			camera->callVoid("setParam", kCameraLensYID,
							 DEFAULT_CAMERA_LENSY);
		} catch (ALError &e){
			log->error("ALImageTranscriber", "Couldn't set Lens Correction Y AGAIN");
		}
	}
}


void ALImageTranscriber::waitForImage ()
{
    try {
#ifdef DEBUG_IMAGE_REQUESTS
        printf("Requesting local image of size %ix%i, color space %i\n",
               IMAGE_WIDTH, IMAGE_HEIGHT, NAO_COLOR_SPACE);
#endif
        ALImage *ALimage = NULL;

        // Attempt to retrieve the next image
        try {
            ALimage = (ALImage*) (camera->call<int>("getDirectRawImageLocal",lem_name));
        }catch (ALError &e) {
            log->error("NaoMain", "Could not call the getImageLocal method of the "
                       "ALVideoDevice module");
        }
        if (ALimage != NULL) {
            memcpy(&image[0], ALimage->getFrame(), IMAGE_BYTE_SIZE);
            //image = ALimage->getFrame();
        }
        else
            cout << "\tALImage from camera was null!!" << endl;

#ifdef DEBUG_IMAGE_REQUESTS
        //You can get some informations of the image.
        int width = ALimage->fWidth;
        int height = ALimage->fHeight;
        int nbLayers = ALimage->fNbLayers;
        int colorSpace = ALimage->fColorSpace;
        long long timeStamp = ALimage->fTimeStamp;
        int seconds = (int)(timeStamp/1000000LL);
        printf("Retrieved an image of dimensions %ix%i, color space %i,"
               "with %i layers and a time stamp of %is \n",
               width, height, colorSpace,nbLayers,seconds);
#endif

        if (image != NULL) {
            // Update Sensors image pointer
            sensors->lockImage();
            sensors->setImage(image);
            sensors->releaseImage();
        }

    }catch (ALError &e) {
        log->error("NaoMain", "Caught an error in run():\n" + e.toString());
    }
}


void ALImageTranscriber::releaseImage(){
    if (!camera_active)
        return;

    //Now you have finished with the image, you have to release it in the V.I.M.
    try
    {
        camera->call<int>( "releaseDirectRawImage", lem_name );
    }catch( ALError& e)
    {
        log->error( "ALImageTranscriber",
                    "could not call the releaseImage method of the ALVideoDevice module" );
    }
}

