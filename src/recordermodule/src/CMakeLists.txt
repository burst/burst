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
PROJECT( RECORDERMODULE )




############################ DEFINITION
# Add here definition needed.
ADD_DEFINITIONS( ${ALCOMMON_DEFINITIONS} ${PTHREAD_DEFINITIONS} ${TINYXML_DEFINITIONS} ${OPENCV_DEFINITIONS} ${BOOST_DEFINITIONS})




############################ INCLUDE DIRECTORY
# Define include directories
INCLUDE_DIRECTORIES( ${PROXIES_INCLUDE_DIR} ${ALCOMMON_INCLUDE_DIR} ${PTHREAD_INCLUDE_DIR}  ${TINYXML_INCLUDE_DIR}  ${OPENCV_INCLUDE_DIR} ${BOOST_INCLUDE_DIR})




############################ PROJECT SOURCES FILES 
# Add here source files needed to compile this project
SET(RECORDERMODULE_SRCS

#<FILES> don't remove this comment
recorder.cpp recorder.h gzstream.cpp gzstream.h
#</FILES> don't remove this comment 

    recordermodule.cpp recordermodule.h
  )



############################ CHECK LIBRARY / EXECUTABLE OPTION

IF( RECORDERMODULE_IS_REMOTE STREQUAL "OFF" )
    MESSAGE( STATUS "recordermodule is compiled as dynamic object" )
    ADD_LIBRARY( recordermodule SHARED ${RECORDERMODULE_SRCS} )
ELSE( RECORDERMODULE_IS_REMOTE STREQUAL "OFF" )
    MESSAGE( STATUS "recordermodule is compiled as remote object" )
    ADD_EXECUTABLE( recordermodule ${RECORDERMODULE_SRCS} )
ENDIF( RECORDERMODULE_IS_REMOTE STREQUAL "OFF" )




############################ SET LIBRARIES TO LINK WITH
TARGET_LINK_LIBRARIES( recordermodule ${ALCOMMON_LIBRARIES} ${PTHREAD_LIBRARIES} ${NEWMAT_LIBRARIES}  ${TINYXML_LIBRARIES}  ${OPENCV_LIBRARIES} ${BOOST_LIBRARIES})




############################ BINARY COPY
# Copy automatically binary to output folder
GET_TARGET_PROPERTY( RECORDERMODULE_LOCATION recordermodule LOCATION)

IF( RECORDERMODULE_IS_REMOTE STREQUAL "OFF" )
  ADD_CUSTOM_COMMAND(
    TARGET recordermodule
    POST_BUILD
    COMMAND ${CMAKE_COMMAND}
    ARGS -E copy
    ${RECORDERMODULE_LOCATION}
    ${OUTPUT_ROOT_DIR_LIB}
  )
ELSE( RECORDERMODULE_IS_REMOTE STREQUAL "OFF" )
  ADD_CUSTOM_COMMAND(
    TARGET recordermodule
    POST_BUILD
    COMMAND ${CMAKE_COMMAND}
    ARGS -E copy
    ${RECORDERMODULE_LOCATION}
    ${OUTPUT_ROOT_DIR_EXE}
  )
ENDIF( RECORDERMODULE_IS_REMOTE STREQUAL "OFF" )


