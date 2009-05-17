//
//  Modified from the Sony SoundPlay demo program.
//
//  This Object is used to store the data of a tone or wav file in memory ready to play.
//  
//
//  Most of this was written by Robin.
//

#ifndef WAV_h_DEFINED
#define WAV_h_DEFINED

#include <OPENR/ODataFormats.h>

enum WAVError {
    WAV_SUCCESS,
    WAV_FAIL,
    WAV_NOT_RIFF,
    WAV_NOT_WAV,
    WAV_FORMAT_NOT_SUPPORTED,
    WAV_CHANNEL_NOT_SUPPORTED,
    WAV_SAMPLINGRATE_NOT_SUPPORTED,
    WAV_BITSPERSAMPLE_NOT_SUPPORTED,
    WAV_SIZE_NOT_ENOUGH,
};

enum WAVType {
    WAV_File,
    WAV_Tone,
    Wav_Failed
};

class WAV {
public:
    WAV();
    WAV(byte* addr);
    ~WAV();

    WAVError CopyTo(OSoundVectorData* data);
    WAVError Rewind();
    WAVError LoadWav(char* FileName);
    WAVError Make(int Mlength, int MFreq);

    int    GetSamplingRate()  { return soundInfo.samplingRate;  }
    int    GetBitsPerSample() { return soundInfo.bitsPerSample; }
    size_t GetSoundUnitSize() { return soundUnitSize;           }

private:
    longword get_longword(byte* addr);
    word     get_word(byte* addr);
    WAVError Set(byte *addr);
    
    // 16KHz 16bits MONO (16 * 2 * 1 * 32ms = 1024)
    static const size_t MONO16K16B_UNIT_SIZE  = 1024;

    static const size_t FMTSIZE_WITHOUT_EXTINFO = 16;
    
    static const double PI2 = 6.283185307179586476925286766559;


    WAVType     ThisWavIs;
    OSoundInfo soundInfo;
    size_t     soundUnitSize;
    byte*      dataStart;
    byte*      dataEnd;
    byte*      dataCurrent;
    ODesignDataID  wavID;
    
};

#endif // WAV_h_DEFINED
