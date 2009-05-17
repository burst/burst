//
//  Modified from the Sony SoundPlay demo program.
//
//  This program plays either a tone or wav file on the AIBO robotic dogs.
//  
//  This program should be compiled as is, and have a controlling program send it a message when a sound is required
//  The sound is then automaticly queued up and played whent the speakers are ready.
//
//  Most of this was written by Robin.
//


#ifndef SNDPlay_h_DEFINED
#define SNDPlay_h_DEFINED

#include <OPENR/OObject.h>
#include <OPENR/OSubject.h>
#include <OPENR/OObserver.h>
#include "WAV.h"
#include "def.h"

static const char* const SPEAKER_LOCATOR = "PRM:/r1/c1/c2/c3/s1-Speaker:S1";
static const char* const SPEAKER_LOCATOR_ERS7 = "PRM:/s1-Speaker:S1";

class SNDPlay : public OObject {
public:
    SNDPlay();
    virtual ~SNDPlay() {}

    OSubject*  subject[numOfSubject];
    OObserver* observer[numOfObserver];

    virtual OStatus DoInit   (const OSystemEvent& event);
    virtual OStatus DoStart  (const OSystemEvent& event);
    virtual OStatus DoStop   (const OSystemEvent& event);
    virtual OStatus DoDestroy(const OSystemEvent& event);
    
    void Notify(const ONotifyEvent& event);
    void Ready(const OReadyEvent& event);
    void SNDPlay::QueueSound(int Freq, int length);

private:
    static const size_t SOUND_NUM_BUFFER = 2;
    static const int WAV_Count = 20;
    
    void      OpenSpeaker();
    void      NewSoundVectorData();
    void      LoadWAV();
    void      SetPowerAndVolume();
    
    WAVError  CopyWAVTo(RCRegion* region);
    RCRegion* FindFreeRegion();

    OPrimitiveID   speakerID;
    RCRegion*      region[SOUND_NUM_BUFFER];
    
    WAV*           SoundQ[WAV_Count];
    byte           QEntry;
    byte           QExit;
};

#endif // SNDPlay_h_DEFINED
