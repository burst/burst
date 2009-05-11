/**
 * \mainpage
 * \section Author
 * @author Patrick de Pas and Olivier Leroy
 *
 * \section Copyright
 * Aldebaran Robotics (c) 2007 All Rights Reserved - This is an example of use.\n
 * Version : $Id$
 *
 * \section Description
 * Module list :  - STMOBJECT_NAME
 */

#ifndef _WIN32
# include <signal.h>
#else
# include <signal.h>
#endif

#include "altypes.h"
#include "alxplatform.h"
#include "recordermodule.h"
#include "albrokermanager.h"

using namespace std;
using namespace AL;


#include "recorder.h"

recorder *lrecorder;


#ifdef RECORDERMODULE_IS_REMOTE_OFF

#ifdef _WIN32
# define ALCALL __declspec(dllexport)
#else
# define ALCALL
#endif

#ifdef __cplusplus
extern "C"
{
#endif


  ALCALL int _createModule (ALPtr < ALBroker > pBroker)
  {
    // init broker with the main broker inctance 
    // from the parent executable
    ALBrokerManager::setInstance (pBroker->fBrokerManager.lock ());
    ALBrokerManager::getInstance ()->addBroker (pBroker);


    // create modules instance
    ALModule::createModule < recorder > (pBroker, "recorder");

    return 0;
  }

  ALCALL int _closeModule ()
  {
    // Delete module instance

    return 0;
  }

# ifdef __cplusplus
}
# endif

#else

void
_terminationHandler (int signum)
{
  std::cout << "Exiting RECORDERMODULE." << std::endl;
  AL::ALBrokerManager::getInstance ()->killAllBroker ();
  ::exit (0);
}


int
usage (char *progName)
{
  std::cout << progName << ", a remote module of naoqi !" << std::endl
    << "USAGE :" << std::endl
    << "-b\t<ip> : binding ip of the server. Default is 127.0.0.1" << std::
    endl << "-p\t<port> : binding port of the server. Default is 9559" <<
    std::
    endl << "-pip\t<ip> : ip of the parent broker. Default is 127.0.0.1" <<
    std::
    endl << "-pport\t<ip> : port of the parent broker. Default is 9559" <<
    std::endl << "-h\t: Display this help\n" << std::endl;
  return 0;
}

int
main (int argc, char *argv[])
{
  std::cout << "..::: starting RECORDERMODULE rerecorder :::.." << std::endl;
  //std::cout << "Copyright (c) 2007, Aldebaran-robotics" << std::endl << std::endl;

  int i = 1;
  std::string brokerName = "recordermodule";
  std::string brokerIP = "";
  int brokerPort = 0;
  // Default parent broker IP
  std::string parentBrokerIP = "127.0.0.1";
  // Default parent broker port
  int parentBrokerPort = kBrokerPort;

  // checking options
  while (i < argc)
    {
      if (argv[i][0] != '-')
	return usage (argv[0]);
      else if (std::string (argv[i]) == "-b")
	brokerIP = std::string (argv[++i]);
      else if (std::string (argv[i]) == "-p")
	brokerPort = atoi (argv[++i]);
      else if (std::string (argv[i]) == "-pip")
	parentBrokerIP = std::string (argv[++i]);
      else if (std::string (argv[i]) == "-pport")
	parentBrokerPort = atoi (argv[++i]);
      else if (std::string (argv[i]) == "-h")
	return usage (argv[0]);
      i++;
    }

  // If server port is not set
  if (!brokerPort)
    brokerPort = FindFreePort (brokerIP);

  std::cout << "Try to connect to parent Broker at ip :" << parentBrokerIP
    << " and port : " << parentBrokerPort << std::endl;
  std::cout << "Start the server bind on this ip :  " << brokerIP
    << " and port : " << brokerPort << std::endl;

  try
  {
    AL::ALBroker::Ptr broker =
      AL::ALBroker::createBroker (brokerName, brokerIP, brokerPort,
				  parentBrokerIP, parentBrokerPort);
    ALModule::createModule < recorder > (broker, "recorder");
  }
  catch (ALError & e)
  {
    std::
      cout << "-----------------------------------------------------" << std::
      endl;
    std::
      cout << "Creation of broker failed. Application will exit now." << std::
      endl;
    std::
      cout << "-----------------------------------------------------" << std::
      endl;
    std::cout << e.toString () << std::endl;
    exit (0);
  }

# ifndef _WIN32
  struct sigaction new_action;
  /* Set up the structure to specify the new action. */
  new_action.sa_handler = _terminationHandler;
  sigemptyset (&new_action.sa_mask);
  new_action.sa_flags = 0;

  sigaction (SIGINT, &new_action, NULL);
# endif

  while (1)
    {
      SleepMs (100);
    }

# ifdef _WIN32
  _terminationHandler (0);
# endif

  exit (0);
}
#endif
