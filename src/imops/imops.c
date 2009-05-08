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

