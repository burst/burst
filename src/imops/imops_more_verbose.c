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

inline unsigned char clip(float a) {
    return a > 255 ? 255 : (a < 0 ? 0 : a);
}

typedef struct {
    float R, G, B;
} RGB;

RGB one(float Y, float U, float V) {
    RGB ret;
    ret.B = 1.164*(Y - 16)                   + 2.018*(U - 128);
    ret.G = 1.164*(Y - 16) - 0.813*(V - 128) - 0.391*(U - 128);
    ret.R = 1.164*(Y - 16) + 1.596*(V - 128);
    return ret;
}

/* We assume that yuv and rgb are both readable and writable, and preallocated.
rgb needs to be 1.5 times size!
*/
void yuv422_to_rgb888(unsigned char* yuv, unsigned char* rgb, int size, int rgb_size)
{
    unsigned char y1, u, y2, v;
    RGB ret;
    if (rgb_size != size * 3 / 2) {
        printf("yuv422_to_rgb888: ERROR, rgb array not of correct size, expected %d, got %d. doing nothing.\n", size * 3 / 2, rgb_size);
        return;
    }
    for (;size > 0; yuv+=4, rgb+=6, size-=4) {
        //u = yuv[0]; y1 = yuv[1]; v = yuv[2]; y2 = yuv[3];
        y1 = yuv[0]; u = yuv[1]; y2 = yuv[2]; v = yuv[3];
        // yuv[0] = u, yuv[1] = v
        // u and v are +-0.5
        ret = one(y1, u, v);
        rgb[0] = clip(ret.R);
        rgb[1] = clip(ret.G);
        rgb[2] = clip(ret.B);

        ret = one(y2, u, v);
        rgb[3] = clip(ret.R);
        rgb[4] = clip(ret.G);
        rgb[5] = clip(ret.B);

    }
}

//        // Conversion
//// Wikipedia on YUV
//#define M13 1.13983
//#define M22 -0.39465
//#define M23 -0.58060
//#define M32 2.03211
//
//// Another source
////#define M13 1.370705
////#define M22 -0.337633
////#define M23 -0.698001
////#define M32 1.732446
//        rgb[0] = y1 + M13 * v;
//        rgb[1] = y1 + M23 * v + M22 * u;
//        rgb[2] = y1 + M32 * u;
//        rgb[3] = y2 + M13 * v;
//        rgb[4] = y2 + M23 * v + M22 * u;
//        rgb[5] = y2 + M32 * u;

