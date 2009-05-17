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

#include <OPENR/OPENRAPI.h>
#include <OPENR/OSyslog.h>
#include <OPENR/core_macro.h>
#include "SNDPlay.h"

SNDPlay::SNDPlay() : speakerID(oprimitiveID_UNDEF)
{
    for (unsigned int i = 0; i < SOUND_NUM_BUFFER; i++) region[i] = 0;
    
    for (int Z = 0; Z < WAV_Count; Z++){
        SoundQ[Z] = NULL;
    }
    
}

OStatus
SNDPlay::DoInit(const OSystemEvent& /*event*/)
{
    //OSYSDEBUG(("SNDPlay::DoInit()\n"));

    NEW_ALL_SUBJECT_AND_OBSERVER;
    REGISTER_ALL_ENTRY;
    SET_ALL_READY_AND_NOTIFY_ENTRY;
    
    QEntry = QExit = 0;
    
    
    OpenSpeaker();
    NewSoundVectorData();
    SetPowerAndVolume();

    return oSUCCESS;
}

OStatus
SNDPlay::DoStart(const OSystemEvent& /*event*/)
{
    //OSYSDEBUG(("SNDPlay::DoStart()\n"));
    
    ENABLE_ALL_SUBJECT;
    ASSERT_READY_TO_ALL_OBSERVER;
    
    //This just loads the starting tones....
    LoadWAV();
    
    return oSUCCESS;
}

OStatus
SNDPlay::DoStop(const OSystemEvent& /*event*/)
{
    //OSYSDEBUG(("SNDPlay::DoStop()\n"));
    
    //Clear the Q...
    QExit = QEntry;
    
    DISABLE_ALL_SUBJECT;
    DEASSERT_READY_TO_ALL_OBSERVER;

    return oSUCCESS;
}

OStatus
SNDPlay::DoDestroy(const OSystemEvent& /*event*/)
{
    DELETE_ALL_SUBJECT_AND_OBSERVER;
    return oSUCCESS;
}

void
SNDPlay::Ready(const OReadyEvent& /*event*/)
{
    //OSYSDEBUG(("SNDPlay::Ready()\n"));
    
    if (QEntry != QExit) {
        
        RCRegion* rgn = FindFreeRegion();
        if (CopyWAVTo(rgn) == WAV_SUCCESS) {
            subject[sbjSpeaker]->SetData(rgn);
        }
        subject[sbjSpeaker]->NotifyObservers();
    }
    
}

void
SNDPlay::OpenSpeaker()
{
    OStatus result;
    char design[orobotdesignNAME_MAX+1];

    result = OPENR::GetRobotDesign(design);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "SNDPlay::OpenSpeaker()",
                  "OPENR::GetRobotDesign() FAILED", result));
    }

    if (strcmp(design, "ERS-7") == 0) {
        result = OPENR::OpenPrimitive(SPEAKER_LOCATOR_ERS7, &speakerID);
    } else { // ERS-210 or ERS-220
        result = OPENR::OpenPrimitive(SPEAKER_LOCATOR, &speakerID);
    }

    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "SNDPlay::OpenSpeaker()",
                  "OPENR::OpenPrimitive() FAILED", result));
    }
}

void
SNDPlay::NewSoundVectorData()
{
    OStatus result;
    MemoryRegionID    soundVecDataID;
    OSoundVectorData* soundVecData;

    size_t soundUnitSize = 1024;

    for (unsigned int i = 0; i < SOUND_NUM_BUFFER; i++) {

        result = OPENR::NewSoundVectorData(1, soundUnitSize,
                                           &soundVecDataID, &soundVecData);
        if (result != oSUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s %d",
                      "SNDPlay::NewSoundVectorData()",
                      "OPENR::NewSoundVectorData() FAILED", result));
            return;
        }

        soundVecData->SetNumData(1);
        soundVecData->GetInfo(0)->Set(odataSOUND_VECTOR,
                                      speakerID, soundUnitSize);

        region[i] = new RCRegion(soundVecData->vectorInfo.memRegionID,
                                 soundVecData->vectorInfo.offset,
                                 (void*)soundVecData,
                                 soundVecData->vectorInfo.totalSize);
    }
}

void
SNDPlay::QueueSound(int Freq, int length){
    
    if ((QEntry+1)%WAV_Count == QExit) return; //The Queue is full.
    if (Freq <0) return; //bad freq value..
    if (Freq >8000) return; // Bad again.
    if (Freq < 10){ // This means we play a Sound File...
        
        //Create the new Wav Object
        SoundQ[QEntry] = new(WAV);
        
        //Now load the wav into mem..
        char File[] = "SNDPlay_WAV1";
        File[11] = 0x30+Freq; //Select the correct file, then load it..
        
        WAVError error = SoundQ[QEntry]->LoadWav(File);
    
        if (error != WAV_SUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s %d",
                      "SNDPlay::LoadWAV()",
                      "wav.Set() FAILED", error));
            delete SoundQ[QEntry];
        }
        else {
            //Increase the Q..
            QEntry = (QEntry+1) % WAV_Count;
        }
    }
    else if (length > 0){
        //Create the new Wav Object
        SoundQ[QEntry] = new(WAV);
        
        //And make the needed SIN function..
        WAVError error = SoundQ[QEntry]->Make(length, Freq);
        
        if (error != WAV_SUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s %d",
                      "SNDPlay::MakeWAV() Failed",
                      Freq, error));
            delete SoundQ[QEntry];
        }
        else {
            //Increase the Q..
            QEntry = (QEntry+1) % WAV_Count;
        }
    }
    
    //If there wasn't anything on the Q, we need to fill the buffers so we get a nice sound...
    if ((QExit+1)%WAV_Count == QEntry){
        //Quick sanity check so we won't crash the system by sending to something not ready..
        if (subject[sbjSpeaker]->IsAnyReady()){
            for (unsigned int i = 0; i < SOUND_NUM_BUFFER; i++) {
                if (region[i]->NumberOfReference() == 1){
                    if (CopyWAVTo(region[i]) == WAV_SUCCESS)
                        subject[sbjSpeaker]->SetData(region[i]);
                }
            }
        }
        subject[sbjSpeaker]->NotifyObservers();
    }
}


void 
SNDPlay::LoadWAV()
{
    //Below 10 is a sound file, length is ignored.
    //Above is a freq, length is in ms
    
    //The init sound..
    QueueSound(500,500);
    QueueSound(1000,100);
}

void
SNDPlay::SetPowerAndVolume()
{
    OStatus result;

    result = OPENR::ControlPrimitive(speakerID,
                                     oprmreqSPEAKER_MUTE_ON, 0, 0, 0, 0);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "SNDPlay::SetPowerAndVolume()", 
                  "OPENR::ControlPrimitive(SPEAKER_MUTE_ON) FAILED", result));
    }

    result = OPENR::SetMotorPower(opowerON);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "SNDPlay::SetPowerAndVolume()", 
                  "OPENR::SetMotorPower() FAILED", result));
    }

    result = OPENR::ControlPrimitive(speakerID,
                                     oprmreqSPEAKER_MUTE_OFF, 0, 0, 0, 0);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "SNDPlay::SetPowerAndVolume()", 
                  "OPENR::ControlPrimitive(SPEAKER_MUTE_OFF) FAILED", result));
    }

    OPrimitiveControl_SpeakerVolume volume(ospkvol10dB);
    result = OPENR::ControlPrimitive(speakerID,
                                     oprmreqSPEAKER_SET_VOLUME,
                                     &volume, sizeof(volume), 0, 0);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "SNDPlay::SetPowerAndVolume()", 
                  "OPENR::ControlPrimitive(SPEAKER_SET_VOLUME) FAILED",
                  result));
    }

    //if (wav.GetSamplingRate() == 16000 && wav.GetBitsPerSample() == 16) {
        OPrimitiveControl_SpeakerSoundType soundType(ospksndMONO16K16B);
        result = OPENR::ControlPrimitive(speakerID,
                                         oprmreqSPEAKER_SET_SOUND_TYPE,
                                         &soundType, sizeof(soundType), 0, 0);
        if (result != oSUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s %d",
                      "SNDPlay::SetPowerAndVolume()", 
                      "OPENR::ControlPrimitive(SPEAKER_SET_SOUND_TYPE) FAILED",
                      result));
        }
    //}
}

WAVError
SNDPlay::CopyWAVTo(RCRegion* rgn)
{
    OSoundVectorData* soundVecData = (OSoundVectorData*)rgn->Base();
    
    WAVError error = SoundQ[QExit]->CopyTo(soundVecData);
    if (error != WAV_SUCCESS) {
        
        //We only want to play the sound once...
        //SoundQ[QExit]->.Rewind();
        
        //Remove the played sound from RAM
        if (SoundQ[QExit] != NULL){
            delete SoundQ[QExit];
            SoundQ[QExit] = NULL;
        }
        
        //Remove the item from the Q..
        QExit = (QExit+1) % WAV_Count;
        
        //If there's something still on the Q, start playing it..
        if (QExit != QEntry){
            error = SoundQ[QExit]->CopyTo(soundVecData);
        }
    }
    return error;
}

RCRegion*
SNDPlay::FindFreeRegion()
{
    //Find ther first section of shared memory which isn't currently being used..
    for (unsigned int i = 0; i < SOUND_NUM_BUFFER; i++) {
        if (region[i]->NumberOfReference() == 1) return region[i];
    }

    return 0;
}

void
SNDPlay::Notify(const ONotifyEvent& event)
{
    const char* text = (const char *)event.Data(0);
    int Val1;
    int Val2;
    
    sscanf (text,"%d %d",&Val1,&Val2);

    
    //OSYSPRINT(("SampleObserver::Notify() [%d %d]\n", Val1, Val2));
    
    //Freq then length
    QueueSound(Val1,Val2);
    observer[event.ObsIndex()]->AssertReady();
}

