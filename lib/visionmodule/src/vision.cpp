#include <iostream>
#include "opencv/cv.h"
#include "opencv/highgui.h"
#include "alproxy.h"
#include "alvisiondefinitions.h"
#include "alvisionimage.h"
#include "vision.h"

#include "almotionproxy.h"
#include <sys/time.h>
#include <time.h>

using namespace std;
using namespace AL;

//______________________________________________
// constructor
//______________________________________________
vision::vision( ALPtr<ALBroker> pBroker, std::string pName ): ALModule(pBroker , pName )
{
  // Describe the module here
  setModuleDescription( "This is the vision module (or at least some early version of it...)." );

  // Define callable methods with there description
  functionName( "registerToVIM","vision", "Register to the V.I.M." );
  BIND_METHOD( vision::registerToVIM );

  functionName( "unRegisterFromVIM","vision", "Unregister from the V.I.M." );
  BIND_METHOD( vision::unRegisterFromVIM );

  functionName( "setCamera", "vision" ,  "select the current camera (0 - top, 1 - bottom)." );
  BIND_METHOD( vision::setCamera );

  functionName( "getBalls","vision", "Get the balls' rect (within the field area!). To be used if the visionmodule is a local module." );
  BIND_METHOD( vision::getBalls );

  functionName( "start", "vision" ,  "Starts the vision task." );
  BIND_METHOD( vision::start );

  functionName( "stop", "vision" ,  "Stops the vision task." );
  BIND_METHOD( vision::stop );

  functionName( "testRemote","vision", "Test remote image acquisition." );
  BIND_METHOD( vision::testRemote );

  functionName( "saveImage","vision", "Save an image received from the camera." );
  addParam( "pName", "path of the picture" );
  BIND_METHOD( vision::saveImage );

  functionName( "saveImageRaw","vision", "Save a raw image received from the camera." );
  BIND_METHOD( vision::saveImageRaw );

  functionName( "saveImageRemote","vision", "Save an image received from the camera. to be used if the visionmodule is a remote module." );
  addParam( "pName", "path of the picture" );
  BIND_METHOD( vision::saveImageRemote );

  //Create a proxy on logger module
  try
  {
    log = getParentBroker()->getLoggerProxy();
    //log->logInFile(true, "test.txt", "lowinfo");
  }catch( ALError& e)
  {
    std::cout << "could not create a proxy to ALLogger module" << std::endl;
  }

  //Create a proxy on memory module
  try
  {
    memory = getParentBroker()->getMemoryProxy();
  }catch( ALError& e)
  {
    std::cout << "could not create a proxy to ALMemory module" << std::endl;
  }

  //Create a proxy on the video input module
  try
  {
    camera = getParentBroker()->getProxy( "NaoCam" );
  }catch( ALError& e )
  {
    log->error( "vision", "could not create a proxy to NaoCam module" );
  }

  storage = cvCreateMemStorage(0);
}


//______________________________________________
// version
//______________________________________________
std::string vision::version()
{
  return ALTOOLS_VERSION( VISIONMODULE );
}



//______________________________________________
// destructor
//______________________________________________
vision::~vision()
{

}


/**
 * registerToVIM
 */
void vision::registerToVIM()
{
  //First you have to choose a unique name for your G.V.M.
  name = "vision_GVM";

  //specification of the resolution among :
  // kVGA ( 640 * 480 ), kQVGA ( 320 * 240 ), kQQVGA ( 160 * 120 ).
  // ( definitions included in alvisiondefinitions.h )
  resolution = kQVGA; //kQVGA

  //specification of the color space desired among :
  //  kYuvColorSpace, kyUvColorSpace, kyuVColorSpace,
  //  kYUVColorSpace, kYUV422InterlacedColorSpace, kRGBColorSpace.
  // ( definitions contained in alvisiondefinitions.h )
  colorSpace = kBGRColorSpace; //kRGBColorSpace

  //minimal number of frames per second ( fps ) required among: 5, 10, 15, and 30 fps.
  int fps = 30;

  //You only have to call the function "register" with required parameters for your process
  try
  {
	log->info( "vision", "registering module, under " + name + " name." );
    name = camera->call<std::string>( "register", name, resolution, colorSpace, fps );
    log->info( "vision", "module registered under " + name + " name." );
  }catch( ALError& e )
  {
    log->error( "vision", "could not call the register method of the NaoCam module" );
  }
}


/**
 * unRegisterFromVIM
 */
void vision::unRegisterFromVIM()
{
  try
  {
  	log->info( "vision", "try to unregister " + name + " module." );
    camera->callVoid( "unRegister", name );
    log->info( "vision", "Done.");
  }catch( ALError& e )
  {
    log->error( "vision", "could not call the unregister method of the " + name +" module" );
  }
}

/**
 * setCamera : select the current camera.
 * @param whichCam index of the camera (0 - top, 1 - bottom)
 */
void vision::setCamera(int whichCam) {
	int currentCam =  camera->call<int>( "getParam", kCameraSelectID );
	if (whichCam != currentCam) {
		camera->callVoid( "setParam", kCameraSelectID, whichCam);
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
}


/**
 * saveImageRaw : save the last image received (raw).
 */
// Copied from VisionDef.h
#define NAO_IMAGE_WIDTH      320
#define NAO_IMAGE_HEIGHT     240
#define IMAGE_BYTE_SIZE    (NAO_IMAGE_WIDTH * NAO_IMAGE_HEIGHT * 2)
void vision::saveImageRaw(){

  //First you have to declare an ALVisionImage to get the video buffer.
  // ( definition included in alvisiondefinitions.h and alvisiondefinitions.cpp )
  ALVisionImage* imageIn;

  //Now you can get the pointer to the video structure.
  try
  {
    imageIn = ( ALVisionImage* ) ( camera->call<int>( "getDirectRawImageLocal", name ) );
  }catch( ALError& e)
  {
    log->error( "vision", "could not call the getImageLocal method of the NaoCam module" );
  }

  std::cout<< imageIn->toString();

    static int saved_frames = 0;
    int MAX_FRAMES = 150;
    if (saved_frames > MAX_FRAMES)
        return;

    string EXT(".NFRM");
    string BASE("/");
    int NUMBER = saved_frames;
    string FOLDER("/home/root/frames");
    stringstream FRAME_PATH;

    FRAME_PATH << FOLDER << BASE << NUMBER << EXT;
    fstream fout(FRAME_PATH.str().c_str(), fstream::out);

    // Retrive joints
    //vector<float> joints = getVisionBodyAngles();

    // Lock and write image
    fout.write(reinterpret_cast<const char*>(imageIn->getFrame()), IMAGE_BYTE_SIZE);

    // Write joints
    //for (vector<float>::const_iterator i = joints.begin(); i < joints.end();
    //     i++) {
    //    fout << *i << " ";
    //}

    // Write sensors
    //vector<float> sensor_data = getAllSensors();
    //for (vector<float>::const_iterator i = sensor_data.begin();
    //     i != sensor_data.end(); i++) {
    //    fout << *i << " ";
    //}

    fout.close();
    cout << "Saved frame #" << saved_frames++ << endl;

    //Now you have finished with the image, you have to release it in the V.I.M.
    try {
        camera->call<int>( "releaseDirectRawImage", name );
    } catch (ALError& e) {
        log->error( "vision", "could not call the releaseImage method of the NaoCam module" );
    }
}



/**
 * saveImage : save the last image received.
 * @param pName path of the file
 */
void vision::saveImage( std::string pName ){

  //First you have to declare an ALVisionImage to get the video buffer.
  // ( definition included in alvisiondefinitions.h and alvisiondefinitions.cpp )
  ALVisionImage* imageIn;

  //Now you can get the pointer to the video structure.
  try
  {
    imageIn = ( ALVisionImage* ) ( camera->call<int>( "getImageLocal", name ) );
  }catch( ALError& e)
  {
    log->error( "vision", "could not call the getImageLocal method of the NaoCam module" );
  }

  std::cout<< imageIn->toString();

  //You can get some informations of the image.
  int width = imageIn->fWidth;
  int height = imageIn->fHeight;
  int nbLayers = imageIn->fNbLayers;
  int colorSpace = imageIn->fColorSpace;
  long long timeStamp = imageIn->fTimeStamp;
  int seconds = (int)(timeStamp/1000000LL);

  //You can get the pointer of the image.
  uInt8 *dataPointerIn = imageIn->getFrame();

  // now you create an openCV image and you save it in a file.
  IplImage* image = cvCreateImage( cvSize( width, height ), 8, nbLayers );

//  image->imageData = ( char* ) imageIn->getFrame();
  image->imageData = ( char* ) dataPointerIn;

  const char* imageName = ( pName + DecToString(seconds) + ".jpg" ).c_str();

  cvSaveImage( imageName, image );
  cvReleaseImage( &image );

  //Now you have finished with the image, you have to release it in the V.I.M.
  try
  {
    camera->call<int>( "releaseImage", name );
  }catch( ALError& e)
  {
    log->error( "vision", "could not call the releaseImage method of the NaoCam module" );
  }

}


/**
 * saveImageRemote : test remote image
 * @param pName path of the file
 */
void vision::testRemote(){

  //Now you can get the pointer to the video structure.
  ALValue results;
  results.arraySetSize(7);

  try
  {
    results = ( camera->call<ALValue>( "getImageRemote", name ) );
  }catch( ALError& e)
  {
    log->error( "vision", "could not call the getImageRemote method of the NaoCam module" );
  }

  if (results.getType()!= ALValue::TypeArray) return;

  const char* dataPointerIn =  static_cast<const char*>(results[6].GetBinary());
  int size = results[6].getSize();

  //You can get some informations of the image.
  int width = (int) results[0];
  int height = (int) results[1];
  int nbLayers = (int) results[2];
  int colorSpace = (int) results[3];
  long long timeStamp = ((long long)(int)results[4])*1000000LL + ((long long)(int)results[5]);

  // now you create an openCV image and you save it in a file.
  IplImage* image = cvCreateImage( cvSize( width, height ), 8, nbLayers );

//  image->imageData = ( char* ) imageIn->getFrame();
  image->imageData = ( char* ) dataPointerIn;

  std::string pName = "aaa";

  //const char* imageName = ( pName + DecToString(results[4]) + ".jpg").c_str();
  const char* imageName = ( pName + "test" + ".jpg").c_str();

printf("imageName %s\n", imageName);
  cvSaveImage( imageName, image );
printf("image saved\n");

try
{
  results = ( camera->call<ALValue>( "releaseImage", name ) );
}catch( ALError& e)
{
  log->error( "vision", "could not call the releaseImage method of the NaoCam module" );
}

printf("image memory released\n");

//  cvReleaseImage( &image );
  cvReleaseImageHeader(&image);
printf("image released\n");
printf("testRemote finished\n");
}







/**
 * saveImageRemote : save the last image received. To be used if visionmodule is a remote module.
 * @param pName path of the file
 */
void vision::saveImageRemote( std::string pName ){

  //Now you can get the pointer to the video structure.
  ALValue results;
  results.arraySetSize(7);

  try
  {
    results = ( camera->call<ALValue>( "getImageRemote", name ) );
  }catch( ALError& e)
  {
    log->error( "vision", "could not call the getImageRemote method of the NaoCam module" );
  }

  if (results.getType()!= ALValue::TypeArray) return;

  const char* dataPointerIn =  static_cast<const char*>(results[6].GetBinary());
  int size = results[6].getSize();

  //You can get some informations of the image.
  int width = (int) results[0];
  int height = (int) results[1];
  int nbLayers = (int) results[2];
  int colorSpace = (int) results[3];
  long long timeStamp = ((long long)(int)results[4])*1000000LL + ((long long)(int)results[5]);

  // now you create an openCV image and you save it in a file.
  IplImage* image = cvCreateImage( cvSize( width, height ), 8, nbLayers );

//  image->imageData = ( char* ) imageIn->getFrame();
  image->imageData = ( char* ) dataPointerIn;

  const char* imageName = ( pName + DecToString(results[4]) + ".jpg").c_str();
//  const char* imageName = ( pName + "test" + ".jpg").c_str();

printf("imageName %s\n", imageName);
  cvSaveImage( imageName, image );
printf("image saved\n");

//try
//{
//  results = ( camera->call<ALValue>( "releaseImage", name ) );
//}catch( ALError& e)
//{
//  log->error( "vision", "could not call the releaseImage method of the NaoCam module" );
//}
//
//printf("image memory released\n");

  cvReleaseImage( &image );
//  cvReleaseImageHeader(&image);
  printf("image released\n");
}

CvSeq** vision::getLargestColoredContour(IplImage* src, int iBoxColorValue, int iBoxColorRange, int iBoxSaturationCutoff, int iMinimalArea, CvRect** rect, bool isField) {
    CvSeq** seqhull = new CvSeq*[20];

	CvSeq* contours = NULL; // = cvCreateSeq(CV_SEQ_ELTYPE_POINT, sizeof(CvSeq), sizeof(CvPoint) , storageContours);
	CvSeq* result = NULL;
	CvSize sz = cvSize( src->width & -2, src->height & -2 );
	IplImage* timg = cvCloneImage( src ); // make a copy of input image
	IplImage* pyr = cvCreateImage( cvSize(sz.width/2, sz.height/2), 8, 3 );
	IplImage* tgray = NULL;
	IplImage* img_hsv = NULL;

	// down-scale and upscale the image to filter out the noise (much faster compared to cvSmooth)
	cvPyrDown( timg, pyr, CV_GAUSSIAN_5x5 ); // pyr is temporarily used to keep the smaller (down-scaled) picture 7
	cvPyrUp( pyr, timg, CV_GAUSSIAN_5x5 ); // pyr is upscaled and saved back to timg, with less noise.
	tgray = cvCreateImage( sz, 8, 1 );

	img_hsv = cvCloneImage( timg );
	cvCvtColor(img_hsv, timg, CV_BGR2HSV);

	int thresholdValue = iBoxColorValue; //Hue value
	int thresholdVariance = iBoxColorRange; //Hue range

	// Remove low saturation colors from image (black & white, shadows, highlights)
	IplImage* tBlackAndWhite = cvCreateImage( sz, 8, 1 );
	cvZero(tBlackAndWhite);
	cvSetImageCOI(timg, 2);
	cvCopy(timg, tBlackAndWhite, 0);//since COI is not supported
	cvThreshold(tBlackAndWhite, tBlackAndWhite, iBoxSaturationCutoff, 255, CV_THRESH_BINARY);

	// extract the H color plane
	cvSetImageCOI(timg, 1);
	cvCopy(timg, tgray, 0);//since COI is not supported

	int topValue = thresholdValue+thresholdVariance;
	int bottomValue = thresholdValue-thresholdVariance;

	bool bInverseThreshold = false;

	if (bottomValue < 0) {
		bInverseThreshold = true;
		bottomValue = 360 + bottomValue;
	}

	if (topValue >= 360) {
		bInverseThreshold = true;
		topValue = topValue - 360;
	}

	IplImage* imgOverTrimmed = cvCloneImage( tgray );
	IplImage* imgUnderTrimmed = cvCloneImage( tgray );
	topValue = topValue / 2;
	bottomValue = bottomValue / 2;

	cvThreshold(imgOverTrimmed, imgOverTrimmed, topValue, 255, CV_THRESH_BINARY_INV);
	cvThreshold(imgUnderTrimmed, imgUnderTrimmed, bottomValue, 255, CV_THRESH_BINARY);

	if (!bInverseThreshold) {
		cvAnd(imgOverTrimmed,imgUnderTrimmed,tgray,NULL);
	} else {
		cvOr(imgOverTrimmed,imgUnderTrimmed,tgray,NULL);
	}

	cvThreshold( tgray, tgray, 0, 255, CV_THRESH_BINARY );
	cvAnd(tBlackAndWhite,tgray,tgray,NULL);

	/*int iContourNumber = */
	cvFindContours( tgray, storage, &contours, sizeof(CvContour),
										 CV_RETR_LIST, CV_CHAIN_APPROX_SIMPLE, cvPoint(0,0) );
	CvSeq* max_contour = NULL;
	CvSeq* curr_contour = contours;
	int iMaxSize = -1;
	int iCurrSize = 0;

	while (curr_contour) {
		result = cvApproxPoly(curr_contour, sizeof(CvContour), storage,
		CV_POLY_APPROX_DP, cvContourPerimeter(curr_contour)*0.02, 0 );
		iCurrSize = fabs(cvContourArea(result, CV_WHOLE_SEQ));

		if (result) {
			cvClearSeq(result);
		}

		if (iCurrSize > iMinimalArea) {
			if (iCurrSize >= iMaxSize) {
				max_contour = curr_contour; //result
				iMaxSize = iCurrSize;
			}
		}

		if (curr_contour->h_next == NULL) {
			curr_contour = NULL;
		} else {
			curr_contour = curr_contour->h_next;
		}
	}
    int iCount= 0;
	if (max_contour != NULL) {
		if(isField) {
			(*rect)[iCount] = cvBoundingRect(max_contour);
			seqhull[0] = cvConvexHull2(max_contour, 0, CV_COUNTER_CLOCKWISE, 0);
		}  
	}
    if(!isField) {
        if (contours != NULL) {
            while(contours) {
			    result = cvApproxPoly( contours, sizeof(CvContour), cvCreateMemStorage(0),
						    CV_POLY_APPROX_DP, cvContourPerimeter(contours)*0.02, 0 );

			    iCurrSize = fabs(cvContourArea(result, CV_WHOLE_SEQ));

			    if (iCurrSize > iMinimalArea) {
				    (*rect)[iCount] = cvBoundingRect(contours);
				    seqhull[iCount] = cvConvexHull2(contours, 0, CV_COUNTER_CLOCKWISE, 0);
				    iCount++;
			    }

			    if (contours->h_next == NULL) {
				    contours = NULL;
			    } else {
				    contours = contours->h_next;
			    }
		    }
        }
    }

	// release memory
	if (pyr) cvReleaseImage( &pyr );
	if (tgray) cvReleaseImage( &tgray );
	if (timg) cvReleaseImage( &timg );
	if (img_hsv) cvReleaseImage( &img_hsv );

	if (tBlackAndWhite) cvReleaseImage( &tBlackAndWhite );
	if (imgOverTrimmed) cvReleaseImage( &imgOverTrimmed );
	if (imgUnderTrimmed) cvReleaseImage( &imgUnderTrimmed );

	pyr = NULL;
	tgray = NULL;
	timg = NULL;
	img_hsv = NULL;
	tBlackAndWhite = NULL;
	imgOverTrimmed = NULL;
	imgUnderTrimmed = NULL;

	if (contours) {
		cvClearSeq(contours);
		contours = NULL;
	}

	if (storage) {
    	cvClearMemStorage(storage);
	}

	return seqhull;
}

ALValue vision::getBalls() {

	ALValue resultBallRect;
	resultBallRect.arraySetSize(4);

	resultBallRect[0] = 0;
	resultBallRect[1] = 0;
	resultBallRect[2] = 0;
	resultBallRect[3] = 0;

	//First you have to declare an ALVisionImage to get the video buffer.
	// ( definition included in alvisiondefinitions.h and alvisiondefinitions.cpp )
	ALVisionImage* imageIn;

	//Now you can get the pointer to the video structure.
	try
	{
	imageIn = ( ALVisionImage* ) ( camera->call<int>( "getImageLocal", name ) );
	}catch( ALError& e)
	{
	log->error( "vision", "could not call the getImageLocal method of the NaoCam module" );
	}

	//You can get some informations of the image.
	int width = imageIn->fWidth;
	int height = imageIn->fHeight;
	int nbLayers = imageIn->fNbLayers;
	int colorSpace = imageIn->fColorSpace;
	long long timeStamp = imageIn->fTimeStamp;
	int seconds = (int)(timeStamp/1000000LL);

//	log->info( "vision", "Creating OpenCV image" );

	//You can get the pointer of the image.
	uInt8 *dataPointerIn = imageIn->getFrame();

	// now you create an openCV image and you save it in a file.
	IplImage* src = cvCreateImage( cvSize( width, height ), 8, nbLayers );

	//  src->imageData = ( char* ) imageIn->getFrame();
	src->imageData = ( char* ) dataPointerIn;

//log->info( "vision", "Searching field" );

	IplImage* mask = 0;
	IplImage* imageClipped = 0;

	// Get field
	CvRect* fieldRect = new CvRect[1];

//printf("before getLargestColoredContour\n");
	// Green field
	// parameters for pan/tilt camera
	//CvSeq* field = getLargestColoredContour(src, 155, 5, 100, 300, fieldRect);
	// parameters for Nao camera in lab
//    CvSeq* field = getLargestColoredContour(src, 175, 30, 25, 1000, fieldRect);
    // Params for WEBOTS
    CvSeq* field = getLargestColoredContour(src, 125, 30, 25, 100, &fieldRect, 1)[0];

    if (field != NULL) {
//    	printf("Field: %d, %d, %d, %d\n", fieldRect.x, fieldRect.y, fieldRect.width, fieldRect.height);

//log->info( "vision", "Searching ball1" );

		CvSize imageSize = cvSize(src->width, src->height);
		mask = cvCreateImage( imageSize, 8, 1 );
		cvZero(mask);

		CvScalar colorWHITE = CV_RGB(255, 255, 255);

		int elementCount = field->total;
		CvPoint* temp = new CvPoint[elementCount];
		CvPoint pt0 = **CV_GET_SEQ_ELEM( CvPoint*, field, elementCount - 1 );
		for (int i = 0; i < elementCount; i++) {
			CvPoint pt = **CV_GET_SEQ_ELEM( CvPoint*, field, i );
			temp[i].x = pt.x;
			temp[i].y = pt.y;
		}
		cvFillConvexPoly(mask, temp, elementCount, colorWHITE, 8, 0);

		imageClipped = cvCreateImage( imageSize, 8, 3 );
		cvZero(imageClipped);
		cvCopy(src, imageClipped, mask);

		// Get ball
		CvRect* ballRect= new CvRect[10];

//log->info( "vision", "Searching ball2" );
	    // parameters for pan/tilt camera
	    //getLargestColoredContour(imageClipped, 17, 10, 100, 50, ballRect);
	    // parameters for Nao camera in lab
//		CvSeq* ballHull = getLargestColoredContour(imageClipped, 40, 25, 50, 30, ballRect);
		// Params for webots
		CvSeq** ballHull = getLargestColoredContour(imageClipped, 55, 125, 50, 30, &ballRect, 0);

//log->info( "vision", "Searching ball3" );
        int* X_Arr= new int[10];
        int* Y_Arr= new int[10];
        int* Width_Arr= new int[10];
        int* Height_Arr= new int[10];

        for(int i=0; ballHull[i] != NULL; i++) {
            X_Arr[i]= ballRect[i].x;
            Y_Arr[i]= ballRect[i].y;
            Width_Arr[i]= ballRect[i].width;
            Height_Arr[i]= ballRect[i].height;
        }
		if (ballHull != NULL) {
//			printf("ballrect: %d, %d, %d, %d\n", ballRect.x, ballRect.y, ballRect.width, ballRect.height);
			resultBallRect[0] = X_Arr;
			resultBallRect[1] = Y_Arr;
			resultBallRect[2] = Width_Arr;
			resultBallRect[3] = Height_Arr;

//			printf("Clearing ball Hull\n");
//			cvClearSeq(ballHull);
//			printf("Ball Hull cleared\n");
		} else {
//	    	printf("Ball not found!\n");
			resultBallRect[0] = -2;
			resultBallRect[1] = -2;
			resultBallRect[2] = -2;
			resultBallRect[3] = -2;
		}
    } else {
//    	printf("Field not found!\n");
		resultBallRect[0] = -1;
		resultBallRect[1] = -1;
		resultBallRect[2] = -1;
		resultBallRect[3] = -1;
    }

//    log->info( "vision", "Trying to save ball position" );
//
    memory->insertData("/BURST/Vision/BallX", resultBallRect[0], 0);
    memory->insertData("/BURST/Vision/BallY", resultBallRect[1], 0);
    memory->insertData("/BURST/Vision/BallWidth", resultBallRect[2], 0);
    memory->insertData("/BURST/Vision/BallHeight", resultBallRect[3], 0);
//
//    log->info( "vision", "Saved ball position" );

//    log->info( "vision", "Trying to release resources" );

	// release the image
	cvReleaseImage(&imageClipped);
	cvReleaseImage(&mask);
	cvReleaseImage(&src);

//	log->info( "vision", "Trying to release local image" );
//	printf("vision: Trying to release local image\n");

	//Now you have finished with the image, you have to release it in the V.I.M.
	try {
		camera->call<int>( "releaseImage", name );
	} catch( ALError& e) {
		log->error( "vision", "could not call the releaseImage method of the vision module" );
	}

//	log->info( "vision", "Released local image" );
//	printf("vision: Released local image\n");

	imageIn = NULL;
//	resultBallRect.clear();
//	resultBallRect = NULL;

//	printf("image released\n");
//	log->info( "vision", "Released resources" );

	return resultBallRect;
}

/**
 * dataChanged. Called by ALMemory when subcription
 * has been modified.
 * @param pDataName, name of the suscribed data
 * @param pValue, value of the suscribed data
 * @param pMessage, message written by user during suscription
 */
void vision::dataChanged(const std::string& pDataName, const ALValue& pValue, const std::string& pMessage)
{
  // ===================================== VERY IMPORTANT ============================================
  // Warning: this method will be called every time the data changes: i.e. every 20 ms
  // We must be very sure that the work we do here takes almost no time.
  // If we take more than 20ms we will starve the thread pool and kill NaoQi
  // =================================================================================================

  try {
    ALPtr<AL::ALMemoryProxy> memory = ALPtr<AL::ALMemoryProxy>(getParentBroker()->getMemoryProxy());
    ALPtr<AL::ALMotionProxy> motion = ALPtr<AL::ALMotionProxy>(getParentBroker()->getMotionProxy());

    // ====================================== This is where we do the work ============================
    // get the value of the AngleY from the InertialSensor
    float result = (float)memory->getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",0);
    // send this value without any smoothing directly to the head pitch
    motion->setAngle("HeadPitch",-result);
    // ================================================================================================


    // std::cout << "AngleY: " << result << std::endl;

  } catch(AL::ALError e) {
    std::cout << "Failed to keep head level: " << e.toString() << std::endl;
  }
}

void vision::start(void)
{
  try {
    ALPtr<AL::ALMemoryProxy> memory = ALPtr<AL::ALMemoryProxy>(getParentBroker()->getMemoryProxy());

	  const std::string& strModuleName = getName().c_str();
    std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time";

	  memory->subscribeOnDataChange(
      memoryKeyNameValueChangesEveryCycle,        // the key
      strModuleName,                              // the name of this module
      string("CycleChangedNotification"),         // the name of the notification
      string("dataChanged") );                    // the method to use for the callback

    // make sure we get notifications every change of value. The default would have been every 50ms
    memory->subscribeOnDataSetTimePolicy(memoryKeyNameValueChangesEveryCycle, strModuleName, 0);

	  std::cout << "vision task started." << std::endl;

  } catch(AL::ALError e) {
    std::cout << "Failed to start the vision task: " << e.toString() << std::endl;
  }
}

void vision::stop()
{
  try {
    ALPtr<AL::ALMemoryProxy> memory = ALPtr<AL::ALMemoryProxy>(getParentBroker()->getMemoryProxy());

	  const std::string& strModuleName = getName().c_str();

	  std::string memoryKeyNameValueChangesEveryCycle = "DCM/Time"; // We could also use "Motion/Synchro"
	  memory->unsubscribeOnDataChange( memoryKeyNameValueChangesEveryCycle, string(strModuleName) );

	  std::cout << "vision task stopped." << std::endl;

  } catch(AL::ALError e) {
    std::cout << "Failed to stop the vision task: " << e.toString() << std::endl;
  }
}
