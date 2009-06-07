#ifndef __IMOPS_H__
#define __IMOPS_H__

#include <boost/shared_ptr.hpp>

#ifndef YMAX
// Color Table definitions. The color table is YMAXxUMAXxVMAX, and
// to lookup in it you take a YUV tripplet and shift them with
// YSHIFT, USHIFT and VSHIFT respectively.
#define YMAX 128
#define UMAX 128
#define VMAX 128
#define YSHIFT 1
#define USHIFT 1
#define VSHIFT 1
#endif // YMAX

// forward declarations
class Profiler;
class Sensors;
class NaoPose;
class Vision;
class Threshold;
class Synchro;
class ALImageTranscriber;

// TODO - if this doesn't work nicely, can always add
// some c++ specific functions to return the ptr.


// These are required for both pynaoqi and the robot module.
extern boost::shared_ptr<Profiler> g_profiler;
extern boost::shared_ptr<Sensors> g_sensors;
extern boost::shared_ptr<NaoPose> g_naopose;
extern boost::shared_ptr<Vision> g_vision;
extern Threshold* g_threshold;


// These are module specific - in charge of the thread that
// retrieves the image and calls the vision notifyImage.
extern boost::shared_ptr<Synchro> g_synchro;
extern boost::shared_ptr<ALImageTranscriber> g_imageTranscriber;


extern "C" {
void init_vision();
void update_table(unsigned char bigTable[YMAX][UMAX][VMAX]);
void on_frame(unsigned char* yplane);
};

#endif // __IMOPS_H__

