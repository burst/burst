/* -*- C++ -*- Tell editors this is a C++ file (despite it's .in extension) */
/* This is an auto generated file. Please do not edit it.*/


#ifndef _manconfig_h
#define _manconfig_h




// :::::::::::::::::::::::::::::::::::::::::::::::::::::: Options variables :::..


# define TARGET_HOST_UNKNOWN    0
# define TARGET_HOST_LINUX      1
# define TARGET_HOST_WINDOWS    2
# define TARGET_HOST_MACOSX     3

# define TARGET_HOST TARGET_HOST_LINUX

# if TARGET_HOST == TARGET_HOST_UNKNOWN
#   error "Target host not supported, or badly detected !"
# endif // TARGET_HOST == TARGET_HOST_UNKNOWN

# define MANMODULE_REVISION ""

//
// Debugging flags
//


// Compile as a remote binary, versus a dynamic library (ON/OFF)
#define MAN_IS_REMOTE_OFF
#ifdef  MAN_IS_REMOTE_ON
#  define MAN_IS_REMOTE
#else
#  undef  MAN_IS_REMOTE
#endif

// print about the initialization of the Man class
#define DEBUG_MAN_INITIALIZATION_ON
#ifdef  DEBUG_MAN_INITIALIZATION_ON
#  define DEBUG_MAN_INITIALIZATION
#else
#  undef  DEBUG_MAN_INITIALIZATION
#endif

// print information before each pthreads thread, mutex, or condition call
#define DEBUG_MAN_THREADING_ON
#ifdef  DEBUG_MAN_THREADING_ON
#  define DEBUG_MAN_THREADING
#else
#  undef  DEBUG_MAN_THREADING
#endif

// print when each image is requested from the robot
#define DEBUG_IMAGE_REQUESTS_OFF
#ifdef  DEBUG_IMAGE_REQUESTS_ON
#  define DEBUG_IMAGE_REQUESTS
#else
#  undef  DEBUG_IMAGE_REQUESTS
#endif

// turn on/off vision processing
#define USE_NOGGIN_OFF
#ifdef  USE_NOGGIN_ON
#  define USE_NOGGIN
#else
#  undef USE_NOGGIN
#endif

// turn on/off vision processing
#define USE_VISION_ON
#ifdef  USE_VISION_ON
#  define USE_VISION
#else
#  undef  USE_VISION
#endif

// turn on/off motion actions
#define USE_MOTION_OFF
#ifdef  USE_MOTION_ON
#  define USE_MOTION
#else
#  undef  USE_MOTION
#endif

//switch btwn AlEnactor and NaoEnactor
#define USE_DCM_OFF
#ifdef USE_DCM_OFF
#  undef USE_DCM
#else
#  define USE_DCM
#endif

// Customize image locking configuration.  Man uses locking.
#define USE_SENSORS_IMAGE_LOCKING_ON
#ifdef  USE_SENSORS_IMAGE_LOCKING_ON
#  define USE_SENSORS_IMAGE_LOCKING
#else
#  undef  USE_SENSORS_IMAGE_LOCKING
#endif

// Redirect the standard error to standard out in C++
#define REDIRECT_C_STDERR_ON
#ifdef  REDIRECT_C_STDERR_ON
#  define REDIRECT_C_STDERR
#else
#  undef  REDIRECT_C_STDERR
#endif


// Academics edition flag
#define USE_ACADEMICS_EDITION_ON
#ifdef USE_ACADEMICS_EDITION_ON
#  define USE_ACADEMICS_EDITION
#else
#  undef USE_ACADEMICS_EDITION
#endif

// turn on/off motion actions
#define USING_LAB_FIELD_OFF
#ifdef  USING_LAB_FIELD_ON
#  define USING_LAB_FIELD
#else
#  undef  USING_LAB_FIELD
#endif

#endif // !_manconfig_h




