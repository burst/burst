##############################
#
# WELCOME 
#
# This is the main cmake configuration file 
# associate to your project
# You can define here specific compilation options
# 
# More about cmake : www.cmake.org


############################ PROJECT NAME
PROJECT( VISIONMODULE )




############################ DEFINITION
# Add here definition needed.
ADD_DEFINITIONS( ${ALCOMMON_DEFINITIONS} ${PTHREAD_DEFINITIONS} ${TINYXML_DEFINITIONS} ${OPENCV_DEFINITIONS} ${BOOST_DEFINITIONS})




############################ INCLUDE DIRECTORY
# Define include directories
INCLUDE_DIRECTORIES( ${PROXIES_INCLUDE_DIR} ${ALCOMMON_INCLUDE_DIR} ${PTHREAD_INCLUDE_DIR}  ${TINYXML_INCLUDE_DIR}  ${OPENCV_INCLUDE_DIR} ${BOOST_INCLUDE_DIR})




############################ PROJECT SOURCES FILES 
# Add here source files needed to compile this project
SET(VISIONMODULE_SRCS

#<FILES> don't remove this comment
vision.cpp vision.h 
#</FILES> don't remove this comment 

    visionmodule.cpp visionmodule.h
  )



############################ CHECK LIBRARY / EXECUTABLE OPTION

IF( VISIONMODULE_IS_REMOTE STREQUAL "OFF" )
    MESSAGE( STATUS "visionmodule is compiled as dynamic object" )
    ADD_LIBRARY( visionmodule SHARED ${VISIONMODULE_SRCS} )
ELSE( VISIONMODULE_IS_REMOTE STREQUAL "OFF" )
    MESSAGE( STATUS "visionmodule is compiled as remote object" )
    ADD_EXECUTABLE( visionmodule ${VISIONMODULE_SRCS} )
ENDIF( VISIONMODULE_IS_REMOTE STREQUAL "OFF" )




############################ SET LIBRARIES TO LINK WITH
TARGET_LINK_LIBRARIES( visionmodule ${ALCOMMON_LIBRARIES} ${PTHREAD_LIBRARIES} ${NEWMAT_LIBRARIES}  ${TINYXML_LIBRARIES}  ${OPENCV_LIBRARIES} ${BOOST_LIBRARIES})




############################ BINARY COPY
# Copy automatically binary to output folder
GET_TARGET_PROPERTY( VISIONMODULE_LOCATION visionmodule LOCATION)

IF( VISIONMODULE_IS_REMOTE STREQUAL "OFF" )
  ADD_CUSTOM_COMMAND(
    TARGET visionmodule
    POST_BUILD
    COMMAND ${CMAKE_COMMAND}
    ARGS -E copy
    ${VISIONMODULE_LOCATION}
    ${OUTPUT_ROOT_DIR_LIB}
  )
ELSE( VISIONMODULE_IS_REMOTE STREQUAL "OFF" )
  ADD_CUSTOM_COMMAND(
    TARGET visionmodule
    POST_BUILD
    COMMAND ${CMAKE_COMMAND}
    ARGS -E copy
    ${VISIONMODULE_LOCATION}
    ${OUTPUT_ROOT_DIR_EXE}
  )
ENDIF( VISIONMODULE_IS_REMOTE STREQUAL "OFF" )


