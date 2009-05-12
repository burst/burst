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
PROJECT( BURSTMEMMODULE )



############################ DEFINITION
# Add here definition needed.
ADD_DEFINITIONS( ${ALCOMMON_DEFINITIONS} ${PTHREAD_DEFINITIONS})



############################ INCLUDE DIRECTORY
# Define include directories
INCLUDE_DIRECTORIES( ${PROXIES_INCLUDE_DIR} ${ALCOMMON_INCLUDE_DIR} ${PTHREAD_INCLUDE_DIR})



############################ PROJECT SOURCES FILES 
# Add here source files needed to compile this project
SET(BURSTMEMMODULE_SRCS

#<FILES> don't remove this comment
burstmem.cpp burstmem.h
#</FILES> don't remove this comment 

    burstmemmodule.cpp burstmemmodule.h
  )



############################ CHECK LIBRARY / EXECUTABLE OPTION

IF( BURSTMEMMODULE_IS_REMOTE STREQUAL "OFF" )
    MESSAGE( STATUS "burstmem is compiled as dynamic object" )
    ADD_LIBRARY( burstmem SHARED ${BURSTMEMMODULE_SRCS} )
ELSE( BURSTMEMMODULE_IS_REMOTE STREQUAL "OFF" )
    MESSAGE( STATUS "burstmem is compiled as remote object" )
    ADD_EXECUTABLE( burstmem ${BURSTMEMMODULE_SRCS} )
ENDIF( BURSTMEMMODULE_IS_REMOTE STREQUAL "OFF" )




############################ SET LIBRARIES TO LINK WITH
TARGET_LINK_LIBRARIES( burstmem ${ALCOMMON_LIBRARIES} ${PTHREAD_LIBRARIES} ${NEWMAT_LIBRARIES}  ${TINYXML_LIBRARIES}  ${OPENCV_LIBRARIES} ${BOOST_LIBRARIES})




############################ BINARY COPY
# Copy automatically binary to output folder
GET_TARGET_PROPERTY( BURSTMEMMODULE_LOCATION burstmem LOCATION)

IF( BURSTMEMMODULE_IS_REMOTE STREQUAL "OFF" )
  ADD_CUSTOM_COMMAND(
    TARGET burstmem
    POST_BUILD
    COMMAND ${CMAKE_COMMAND}
    ARGS -E copy
    ${BURSTMEMMODULE_LOCATION}
    ${OUTPUT_ROOT_DIR_LIB}
  )
ELSE( BURSTMEMMODULE_IS_REMOTE STREQUAL "OFF" )
  ADD_CUSTOM_COMMAND(
    TARGET burstmem
    POST_BUILD
    COMMAND ${CMAKE_COMMAND}
    ARGS -E copy
    ${BURSTMEMMODULE_LOCATION}
    ${OUTPUT_ROOT_DIR_EXE}
  )
ENDIF( BURSTMEMMODULE_IS_REMOTE STREQUAL "OFF" )


