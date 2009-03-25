##############################
#
# WELCOME 
#
# This is the main cmake configuration file 
# associate to your project
# You can define here specific compilation options
# 
# More about cmake : www.cmake.org
#
# Using cmake command line : 
# 1. Create a build directory : mkdir build
# 2. Configure cmake project : cd build; cmake ..
#   You can also generate project with your favorite IDE : 
#   Example : Under Mac osx use "cmake .. -G XCode"
#   see cmake help for more information
# 3. Edit project option : ccmake .
# 4. Build it : make 



############################ PROJECT NAME
PROJECT( VISIONMODULE )




############################ VERSION
# Check cMake version
CMAKE_MINIMUM_REQUIRED( VERSION 2.2.0 )




############################ COLORIZE MAKEFILE
# Colorized output
SET( CMAKE_COLOR_MAKEFILE TRUE )




############################ ENVIRONMENT VARIABLE AL_DIR
# Check that AL_DIR is set
# WARNING : Project can not be build 
# or run without the environment variable AL_DIR

IF( "x$ENV{AL_DIR}x" STREQUAL "xx" )
#  SET( ENV{AL_DIR} /opt/aldebaran/info/naoqi )
  MESSAGE( STATUS "Warning variable AL_DIR has not been set !" )
ENDIF( "x$ENV{AL_DIR}x" STREQUAL "xx" )
#SET( AL_DIR "$ENV{AL_DIR}" )

INCLUDE ( ../findroot.cmake )




############################ LIBRARY OR EXECUTABLE?
# Create an option to compile module as a libray
# or as a remote executable
OPTION(  VISIONMODULE_IS_REMOTE
    " visionmodule module is compiled as a remote module (ON or OFF)"
    OFF
  )




############################ CMAKE PACKAGE DIRECTORY
# Set cmakeModules folder
SET( CMAKE_MODULE_PATH ${AL_DIR}/cmakemodules )




############################ ALDEBARAN CMAKE FILE
# Include aldebaran config file 
# (platform management)

INCLUDE( "${CMAKE_MODULE_PATH}/aldebaran.cmake" )


############################ DOXYGEN
# Create an option for doxygen generation
OPTION( DOC_GENERATE
        "Generate documentation (ON or OFF)"
        OFF
      )




############################ DISPLAY
# Display summary of options
MESSAGE( STATUS "" )
MESSAGE( STATUS "...:::: Configuration -  VISIONMODULE ::::..." )
MESSAGE( STATUS "" )




############################ FIND PACKAGE
# Libraries specifics. Define here cmake packages
# usefull to your project

FIND_PACKAGE( Doxygen QUIET )
FIND_PACKAGE( Subversion QUIET )
FIND_PACKAGE( ALCOMMON REQUIRED )
FIND_PACKAGE( TINYXML REQUIRED )
FIND_PACKAGE( PTHREAD REQUIRED )
FIND_PACKAGE( OPENCV REQUIRED )
FIND_PACKAGE( BOOST REQUIRED )



############################ NAOQI LOCATION
# Define main executable location (naoqi)
SET( NAOQI "${AL_DIR}/bin/naoqi" )




############################ OUTPUT LOCATION
# Define output directory.
# doxygen documentation location is set 
# according to the project name
SET( OUTPUT_ROOT_DIR_EXE "${AL_DIR}/modules/bin/" )
SET( OUTPUT_ROOT_DIR_LIB "${AL_DIR}/modules/lib/" )
SET( OUTPUT_ROOT_DIR_DOC "${AL_DIR}/modules/doc/visionmodule/" )




############################ TESTS
# Define main test script location
SET( TEST_RUN "${AL_DIR}/extern/python/aldebaran/test_run.py" )

#<ADD_TEST> don't remove this comment
### test example ADD_TEST(My_test python ${TEST_RUN} -p ${NAOQI} -s ${CMAKE_CURRENT_SOURCE_DIR}/test/myRubyTest.rb)

#</ADD_TEST> don't remove this comment 




############################ DIRECTORIES CREATION
FILE(MAKE_DIRECTORY "${AL_DIR}/modules/doc" )
FILE(MAKE_DIRECTORY "${OUTPUT_ROOT_DIR_DOC}" )




############################ DISPLAY OUPUT DIRECTORY
# uncomment this line to display output directory on cmake configuration
# MESSAGE( STATUS "bin folder : '${OUTPUT_ROOT_DIR_EXE}' | lib folder : '${OUTPUT_ROOT_DIR_LIB}' | doc folder : '${OUTPUT_ROOT_DIR_DOC}'" )




############################ CONFIG.H GENERATION
FIND_FILE( CFG_FILE config.in ${CMAKE_CURRENT_SOURCE_DIR} )

IF( CFG_FILE )
  MESSAGE( STATUS "config.in found (${CFG_FILE})" )
  CONFIGURE_FILE("${CMAKE_CURRENT_SOURCE_DIR}/config.in"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/config.h"
      ESCAPE_QUOTES
  )
ENDIF( CFG_FILE )




############################ SUBDIRECTORIES INCLUSION
# Compile folders
SUBDIRS( src )
SUBDIRS( doc )

