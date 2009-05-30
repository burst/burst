/*
Any image processing operation that is not easy / fast enough to do
in straight python goes into here. They should all be easily callable
using the ctypes wrapper, which I hope will be enought till the end
of this competition.
*/

#include <string.h>

/* Pass a YUV image in 422 through a YUV lookup table
Currently the values for the offsets are hardcoded.
 - but there is a nice function to write to this from outside,
 say from some python code.
*/

#define YMAX 128
#define UMAX 128
#define VMAX 128
#define YSHIFT 1
#define USHIFT 1
#define VSHIFT 1

#define IMAGE_HEIGHT 240
#define IMAGE_WIDTH 320

// Copied from northern bites Vision/VisionDef.h
// THRESHOLD COLORS
#define GREY 0
#define WHITE 1
#define GREEN 2
#define BLUE 3
#define YELLOW 4
#define ORANGE 5
#define YELLOWWHITE 6
#define BLUEGREEN 7
#define ORANGERED 8
#define ORANGEYELLOW 9
#define RED 10
#define NAVY 11
#define BLACK 12
#define PINK 13
#define SHADOW 14
#define CYAN 15
#define DARK_TURQUOISE 16
#define LAWN_GREEN 17
#define PALE_GREEN 18
#define BROWN 19
#define SEA_GREEN 20
#define ROYAL_BLUE 21
#define POWDER_BLUE 22
#define MEDIUM_PURPLE 23
#define MAROON 24
#define LIGHT_SKY_BLUE 25
#define MAGENTA 26
#define PURPLE 27

// index to rgb table
unsigned char indexed_as_rgb[][3] = {
// GREY 0
    {127, 127, 127},
// WHITE 1
    {255, 255, 255},
// GREEN 2
    {10, 74, 10},
// BLUE 3
    {0, 0, 255},
// YELLOW 4
    {200, 200, 32},
// ORANGE 5
    {223, 139, 64},
// YELLOWWHITE 6
    {0, 0, 0},
// BLUEGREEN 7
    {0, 0, 0},
// ORANGERED 8
    {0, 0, 0},
// ORANGEYELLOW 9
    {0, 0, 0},
// RED 10
    {234, 38, 38},
// NAVY 11
    {0, 0, 0},
// BLACK 12
    {0, 0, 0},
// PINK 13
    {0, 0, 0},
// SHADOW 14
    {0, 0, 0},
// CYAN 15
    {0, 0, 0},
// DARK_TURQUOISE 16
    {0, 0, 0},
// LAWN_GREEN 17
    {0, 0, 0},
// PALE_GREEN 18
    {0, 0, 0},
// BROWN 19
    {0, 0, 0},
// SEA_GREEN 20
    {0, 0, 0},
// ROYAL_BLUE 21
    {0, 0, 0},
// POWDER_BLUE 22
    {0, 0, 0},
// MEDIUM_PURPLE 23
    {0, 0, 0},
// MAROON 24
    {0, 0, 0},
// LIGHT_SKY_BLUE 25
    {0, 0, 0},
// MAGENTA 26
    {0, 0, 0},
// PURPLE 27
    {0, 0, 0},

};

void write_index_to_rgb(char* index_to_rgb, int color_start, int color_end) {
    if (color_end < color_start) return;
    if (color_start < 0 || color_end < 0) return;
    if (color_end > sizeof(indexed_as_rgb)/3) return;
    memcpy(&indexed_as_rgb[color_start], index_to_rgb, (color_end-color_start)*3);
}


// threshold
//  bigTable - a Northern bytes YMAX x UMAX x VMAX table, mapping yuv to one byte
// indexed colors.
//  yplane - the start of the YUV422 image, yplane is the first byte, the next
//   planes are either 1 byte ahead or 3 bytes ahead, usually YUYV which means
//   1 and 3 respectively. If inverted, that would be 1, 3.

// thresholded - Threshold.h::Threshold::thresholded
void yuv422_to_thresholded(unsigned char bigTable[YMAX][UMAX][VMAX], unsigned char* yplane, unsigned char thresholded[IMAGE_HEIGHT][IMAGE_WIDTH])
{
    // My loop variables
    int m;
    unsigned char *tPtr, *tEnd, *tOff; // pointers into thresholded array
    const unsigned char *yPtr, *uPtr, *vPtr; // pointers into image array

    // My loop variable initializations
    yPtr = yplane;
    uPtr = yplane + 3; // or is that 3? YES IT IS!
    vPtr = yplane + 1;

    tPtr = &thresholded[0][0];
    tEnd = &thresholded[IMAGE_HEIGHT-1][IMAGE_WIDTH-1] + 1;
    m = (IMAGE_WIDTH * IMAGE_HEIGHT) % 8;

    // number of non-unrolled offset from beginning of row
    tOff = tPtr + m;

    // due to YUV422 data, we can only increment u & v every two assigments
    // thus, we need to do different stuff if we start off with even or odd
    // remainder.  However, we won't get odd # of pixels in 422 (not valid), so
    // lets ignore that

    // here is non-unrolled loop (unrolled by 2, actually)
    while (tPtr < tOff) {
        // we increment Y by 2 every time, and U and V by 4 every two times
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2; uPtr+=4; vPtr+=4;
    }

    // here is the unrolled loop
    while (tPtr < tEnd) {
        // Eight unrolled table lookups
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2; uPtr+=4; vPtr+=4;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2; uPtr+=4; vPtr+=4;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2; uPtr+=4; vPtr+=4;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2;
        *tPtr++ = bigTable[*yPtr>>YSHIFT][*uPtr>>USHIFT][*vPtr>>VSHIFT];
        yPtr+=2; uPtr+=4; vPtr+=4;
    }
}

// Debugging only - image continues with the thresholded image, but
// we need to show ourselves the image, it is much easier with an
// RGB one where the indices have been mapped into the RGB we
// assigned to them earlier (sort of the inverse of thresholding)

void thresholded_to_rgb(unsigned char thresholded[IMAGE_HEIGHT][IMAGE_WIDTH],
    unsigned char rgb[IMAGE_HEIGHT*IMAGE_WIDTH*3])
{
    // rgb output is actually width first, not later, so we keep
    // two pointers
    unsigned char* src = &thresholded[0][0];
    unsigned char* tgt = &rgb[0];
    unsigned char *color;
    int i = IMAGE_HEIGHT*IMAGE_WIDTH;

    for (i = IMAGE_HEIGHT*IMAGE_WIDTH; i > 0; --i, tgt+=3, ++src) {
        color = indexed_as_rgb[*src];
        tgt[0] = color[0];
        tgt[1] = color[1];
        tgt[2] = color[2];
        /*
        if (src_x >= IMAGE_WIDTH) {
            src_x = 0;
            src_y += 1;
            tgt = &rgb[0] + src_y*3;
        }
        */
    }
}


/*
Convert a string of YUY422 to RGB888
YUV422 is converted 4 bytes into two pixels, i.e. 4 bytes -> 6 bytes

the yuv is stores as:
v y1 u y2

where each one is 8 bits, and encodes the relevant values for the whole 2
pixels, except the y's which are one for each pixel.

Note that this is actually Y C_b C_r and not YUV (talking colour spaces)
see for instance http://fourcc.org/fccyvrgb.php
*/
#include <stdio.h>

void init_lookups()
{
    // TODO
}

/* We assume that yuv and rgb are both readable and writable, and preallocated.
rgb needs to be 1.5 times size!
*/
void yuv422_to_rgb888(char* yuv, char* rgb, int size, int rgb_size)
{
    char y1, u, y2, v;
    if (rgb_size != size * 3 / 2) {
        printf("yuv422_to_rgb888: ERROR, rgb array not of correct size, expected %d, got %d. doing nothing.\n", size * 3 / 2, rgb_size);
        return;
    }
    for (;size > 0; yuv+=4, rgb+=6, size-=4) {
        // Main source: wikipedia YUV, some googling (forget where), and
        // The aldebaran forums that convinced me that the order is
        // y1|u|y2|v and not u|y1|v|y2.
        y1 = yuv[0]; u = yuv[1]; y2 = yuv[2]; v = yuv[3];

        // yuv[0] = u, yuv[1] = v
        // u and v are +-0.5
        u -= 128;
        v -= 128;

        // Conversion
        rgb[0] = y1 + 1.370705 * v;
        rgb[1] = y1 - 0.698001 * v - 0.337633 * u;
        rgb[2] = y1 + 1.732446 * u;

        rgb[3] = y2 + 1.370705 * v;
        rgb[4] = y2 - 0.698001 * v - 0.337633 * u;
        rgb[5] = y2 + 1.732446 * u;
        
    }
}

