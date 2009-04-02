#include <signal.h>

#include "altypes.h"
#include "alxplatform.h"
#include "testvision.h"
#include "albrokermanager.h"
#include "alvisionimage.h"
#include "alproxy.h"

using namespace std;
using namespace AL;

AL::ALBroker::Ptr broker;

// do you have to define a module?

class themodule : public AL::ALModule {
public:
    themodule( ALPtr<ALBroker> pBroker, std::string pName );
    virtual ~themodule();
    // are these required?
    std::string version() { return "1.0"; }
    bool innerTest(){ return true;};
};

void tryoutstuff()
{
    //proxy to the logger module
    ALPtr<AL::ALLoggerProxy> log;

    //proxy to the memory module
    ALPtr<AL::ALMemoryProxy> memory;

    //proxy on the video input module
    ALPtr<AL::ALProxy> camera;

    //log = broker->getLoggerProxy(); // seems to be redundant?? is the constructor already doing this? wire capture shows two albroker:exploreToGetModuleByNameResponse requests...
    //memory = broker->getMemoryProxy();
    camera = broker->getProxy( "NaoCam" );

  string name = "testvision_GVM";

  int resolution = kVGA; //kQVGA
  int colorSpace = kRGBColorSpace; //kRGBColorSpace
  int fps = 15;
  name = camera->call<std::string>( "register", name, resolution, colorSpace, fps );

#define NAO_IMAGE_WIDTH      320
#define NAO_IMAGE_HEIGHT     240
#define IMAGE_BYTE_SIZE    (NAO_IMAGE_WIDTH * NAO_IMAGE_HEIGHT * 2)
  ALValue results;
  results = ( camera->call<ALValue>( "getImageRemote", name ) );
  if (results.getType()!= ALValue::TypeArray) { cout << "getImageRemote returned no array! " << results.getType() << "\n"; }
  const char* dataPointerIn =  static_cast<const char*>(results[6].GetBinary());
  int size = results[6].getSize();
  int width = (int) results[0];
  int height = (int) results[1];
  int nbLayers = (int) results[2];
  colorSpace = (int) results[3];
  long long timeStamp = ((long long)(int)results[4])*1000000LL + ((long long)(int)results[5]);
  cout << "got image: " << size << ", " << width << ", " << height << ", " << nbLayers << ", " << colorSpace << "," << timeStamp << "\n";
  results = ( camera->call<ALValue>( "releaseImage", name ) );

#if 0
    { // getdirectrawimagelocal - fails in toString..
        ALVisionImage* imageIn;
        imageIn = ( ALVisionImage* ) ( camera->call<int>( "getDirectRawImageLocal", name ) );
        std::cout<< imageIn->toString(); // segfaults - in asm (i.e. aldebaran code somewhere.. toString
    // do something with the frame here.
    //fout.write(reinterpret_cast<const char*>(imageIn->getFrame()), IMAGE_BYTE_SIZE);
        camera->call<int>( "releaseDirectRawImage", name );
    }
#endif
    // wrapup
    camera->callVoid( "unRegister", name );
}

int main( int argc, char *argv[] )
{
  std::cout << "..::: starting VISIONMODULE revision :::.." << std::endl;
  
  std::string brokerName = "visionmodule";
  std::string brokerIP = "127.0.0.1";
  int brokerPort = 0 ;
  std::string parentBrokerIP = "127.0.0.1";
  int parentBrokerPort = kBrokerPort;

  brokerPort = FindFreePort( brokerIP );     

  for (int i = 1 ; i < argc - 1 ; ++i) {
    if (argv[i][0] == '-' && argv[i][1] == 'p') {
        parentBrokerIP = argv[i+1];
    }
  }

  std::cout << "Try to connect to parent Broker at ip :" << parentBrokerIP
            << " and port : " << parentBrokerPort << std::endl;
  std::cout << "Start the server bind on this ip :  " << brokerIP
            << " and port : " << brokerPort << std::endl;

 try
 {
   //ALModule::createModule<vision>( broker ,  "testvision" );
   broker = AL::ALBroker::createBroker(brokerName, brokerIP, brokerPort, parentBrokerIP, parentBrokerPort);
   //ALModule::createModule<mymodule>( broker ,  "mymodule" );
   tryoutstuff();
 }
 catch(ALError &e)
 {
   std::cout << "-----------------------------------------------------" << std::endl;
   std::cout << "Creation of broker failed. Application will exit now." << std::endl;
   std::cout << "-----------------------------------------------------" << std::endl;
   std::cout << e.toString() << std::endl;
   exit(0);
 }

  while( 1 )
  {
    SleepMs( 100 );
  }

  exit( 0 );
}

