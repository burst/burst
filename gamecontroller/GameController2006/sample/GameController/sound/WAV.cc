//
//  Modified from the Sony SoundPlay demo program.
//
//  This Object is used to store the data of a tone or wav file in memory ready to play.
//  
//
//  Most of this was written by Robin.
//


//#include <OPENR/OPENR.h>
#include <OPENR/OPENRAPI.h>
#include <OPENR/OSyslog.h>
#include "WAV.h"
#include <math.h>

WAV::WAV() : soundInfo(), dataStart(0), dataEnd(0), dataCurrent(0)
{
    ThisWavIs = Wav_Failed;
}

WAV::WAV(byte* addr) : dataStart(0), dataEnd(0), dataCurrent(0)
{
    Set(addr);
}

WAV::~WAV(){
    if (ThisWavIs == Wav_Failed){
        return;
    }else if (ThisWavIs == WAV_File){
        OPENR::DeleteDesignData(wavID);
    }else {
        delete [] dataStart;
    }
}

WAVError
WAV::Make(int Mlength, int MFreq){
    
    // Fake the WAV details...
    soundUnitSize           = MONO16K16B_UNIT_SIZE;
    soundInfo.format        = osoundformatPCM;
    soundInfo.channel       = osoundchannelMONO;
    soundInfo.samplingRate  = 16000;
    soundInfo.bitsPerSample = 16;
    
    // 32 samples about one ms..
    soundInfo.dataSize = Mlength * 32;
    
    //Allocate the amount of memory needed for the wav..
    dataCurrent = dataStart = new byte[soundInfo.dataSize];
    
    dataEnd = dataStart + soundInfo.dataSize;
    
    //Remember what kind of a wave this is so we will destroy fake ones, and not have them being a memory leak.
    ThisWavIs = WAV_Tone;
    
    //Now fill the memory with the required SIN wave.
    if (MFreq < 300 || MFreq > 8000) MFreq = 2000;
    
    //Cal the number of samples needed..
    int Samples = (int) 16000/MFreq;
    
    //Work out what that relates to for a full sign wav.
    double Increments = PI2/Samples;
    
    //Because each sample is two bytes, we need double the values.
    Samples *= 2;
    
    int Value;
    //Now fill the memory array..
    for (unsigned int i=0; i < soundInfo.dataSize; i++){
        Value = (int) ((sin(( ((int)(i/2)) % Samples )*Increments)*26214)+ 32767);
        //Wav files are little endin, so swap the bytes around...
        *(dataStart + i) = (byte) Value;
        *(dataStart + ++i) = (byte) (Value>>8);
    }
    return WAV_SUCCESS;

}


WAVError
WAV::LoadWav(char *FileName) {
    byte*  addr;
    size_t size;

    
    
    //Load the wav file by the name givin in the DesignDB
    OStatus result = OPENR::FindDesignData(FileName,
                                           &wavID, &addr, &size);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d [%s]",
                  "Wav::LoadWAV()",
                  "OPENR::FindDesignData() FAILED", result, FileName));
        return WAV_FAIL;
    }
    
    
    ThisWavIs = WAV_File;
    return Set(addr);
}



WAVError
WAV::Set(byte *addr)
{
    //
    // Check Wav Header
    //
    if (strncmp((char *)addr, "RIFF", 4)) return WAV_NOT_RIFF;
    addr += 4;

    longword length = get_longword(addr);
    addr += sizeof(longword);
    OSYSDEBUG(( "length = %x\n", length));

    if (strncmp((char *)addr, "WAVE", 4)) return WAV_NOT_WAV;
    length -= 4;
    addr += 4;

    //
    // Check Chunk
    //
    while (length > 8) {

        size_t chunksize;
        char *buf = (char *)addr;
    
        addr += 4;

        chunksize = get_longword(addr);
        addr += sizeof(longword);
        length -= chunksize + 8;

        if (!strncmp(buf, "fmt ", 4)) {

            //
            // Format Chunk
            //

            //
            // Check WAV Type
            //
            soundInfo.format = (OSoundFormat)get_word(addr);
            addr += sizeof(word);
            if (soundInfo.format != osoundformatPCM) {
                OSYSDEBUG(("WAV_FORMAT_NOT_SUPPORTED\n"));
                return WAV_FORMAT_NOT_SUPPORTED;
            }

            //
            // Channel
            //
            soundInfo.channel = (OSoundChannel)get_word(addr);
            addr += sizeof(word);
            if (soundInfo.channel != osoundchannelMONO) {
                OSYSDEBUG(("WAV_CHANNEL_NOT_SUPPORTED\n"));
                return WAV_CHANNEL_NOT_SUPPORTED;
            }

            //
            // Sampling Rate
            //
            longword frq = get_longword(addr);
            addr += sizeof(longword);
            soundInfo.samplingRate = (word)frq;
            if (soundInfo.samplingRate != 16000) {
                OSYSDEBUG(("WAV_SAMPLINGRATE_NOT_SUPPORTED\n"));
                return WAV_SAMPLINGRATE_NOT_SUPPORTED;
            }

            //
            // DataSize Per sec
            //
            addr += sizeof(longword);

            //
            // Block Size
            //
            addr += sizeof(word);

            //
            // Bits Of Sample
            //
            soundInfo.bitsPerSample = get_word(addr);
            addr += sizeof(word);
            soundInfo.bitsPerSample *= soundInfo.channel;
            if (soundInfo.bitsPerSample != 16) {
                OSYSDEBUG(("WAV_BITSPERSAMPLE_NOT_SUPPORTED\n"));
                return WAV_BITSPERSAMPLE_NOT_SUPPORTED;
            }

            //
            // Skip Extentded Infomation
            //
            addr += chunksize - FMTSIZE_WITHOUT_EXTINFO;
            
            OSYSDEBUG(( "fmt chunksize = %d\n", chunksize));
            OSYSDEBUG(( "samplingRate  = %d\n", soundInfo.samplingRate));
            OSYSDEBUG(( "bitsPerSample = %d\n", soundInfo.bitsPerSample));
            
        } else if (!strncmp(buf, "data", 4)) {

            //
            // Data Chunk
            //
            OSYSDEBUG(( "data chunksize = %d\n", chunksize));
            soundInfo.dataSize = chunksize;
            dataStart = dataCurrent = addr;
            dataEnd = dataStart + soundInfo.dataSize;
            break;

        } else {

            //
            // Fact Chunk
            //
            addr += chunksize;
        }
    }

    int rate = soundInfo.samplingRate;
    int bits = soundInfo.bitsPerSample;
    if (rate == 16000 & bits == 16) {
        soundUnitSize = MONO16K16B_UNIT_SIZE;
    }
    
    return WAV_SUCCESS;
}

WAVError
WAV::CopyTo(OSoundVectorData* data)
{
    //If we've reached the end of the wav, don't try and copy any more..
    if (dataCurrent >= dataEnd) return WAV_FAIL;
    
    //Get the details of the wav and make sure they are what the speaker is expecting..
    OSoundInfo* sinfo = data->GetInfo(0);
    if (soundUnitSize > sinfo->maxDataSize) {
        OSYSDEBUG(("WAV_SIZE_NOT_ENOUGH "));
        return WAV_SIZE_NOT_ENOUGH;
    }

    sinfo->dataSize      = soundUnitSize;
    sinfo->format        = soundInfo.format;
    sinfo->channel       = soundInfo.channel;
    sinfo->samplingRate  = soundInfo.samplingRate;
    sinfo->bitsPerSample = soundInfo.bitsPerSample;

    //dest is the shared mem that the speaker will play.
    //src is the non shared memory section where the wav is.
    byte* src  = dataCurrent;
    byte* dest = data->GetData(0);
    byte* end;
    
    //See how much of the wav is left to play.
    //note: result must be +ve as we check !(dataCurrent >= dataEnd) above
    unsigned int num = (unsigned int)(dataEnd - dataCurrent);
    
    //If there's more then a standard soundunitsize (normally 1024 bytes..)
    // copy only as much as is the standard soundunitsize.
    if (soundUnitSize <= num) {
    
        end = dest + soundUnitSize; 
        while (dest < end) {
            *dest++ = *src++;
        }
        dataCurrent += soundUnitSize;

    } else {
        //Otherwise copy was much of the wav is left.
        end = dest + num;
        while (dest < end) {
            *dest++ = *src++;
        }
        //Let the speaker know there isn't a full block of data
        memset(dest, 0x0, soundUnitSize - num);
        dataCurrent = dataEnd;
    }

    return WAV_SUCCESS;
}

WAVError
WAV::Rewind()
{
    dataCurrent = dataStart;
    return WAV_SUCCESS;
}

longword
WAV::get_longword(byte* ptr)
{
    longword lw0 = (longword)ptr[0];
    longword lw1 = (longword)ptr[1] << 8;
    longword lw2 = (longword)ptr[2] << 16;
    longword lw3 = (longword)ptr[3] << 24;
    return lw0 + lw1 + lw2 + lw3;
}

word
WAV::get_word(byte* ptr)
{
    word w0 = (word)ptr[0];
    word w1 = (word)ptr[1] << 8;
    return w0 + w1;
}
