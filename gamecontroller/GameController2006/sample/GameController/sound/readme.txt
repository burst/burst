Hi Will,
  I have just zipped up the source to our SNDPlay binary, you should be able to extract the required sound code for tones easily. If you have any problmes let me know, I can get Robin (the guy who wrote it) to actually place the sound code in the game controller binary for you.

These are the connections for sound that we have in our connect.cfg - 
SNDPlay.Speaker.OSoundVectorData.S                            OVirtualRobotAudioComm.Speaker.OSoundVectorData.O
NUbot.SoundCommand.char.S                                     SNDPlay.ReceiveString.char.O

You should only need one connection (along the lines of) -
GameController.Speaker.OSoundVectorData.S	OVirtualRobotAudioComm.Speaker.OSoundVectorData.O

To play a sound when penalised I do (in our binary) ->
  bool doSound = false;
  int tempState = (int)data->state;
  if (tempState != state && tempState == PENALISED) doSound = 1;
  state = tempState;
  if (state==PENALISED && data->teams[!(int)tempTeam].players[*playerIn-1].secsTillUnpenalised <=0) doSound = 2;
  if (doSound > 0) {
    char* SoundCommand = "400 600";
    nubot->subject[sbjSoundCommand]->SetData(SoundCommand, strlen(SoundCommand)+1); 
    nubot->subject[sbjSoundCommand]->NotifyObservers();
  }

The reason for two places where I set doSound is that we beep once when going into penalised (this is the first if, doSound = 1) and then we beep continously when secsTillUnpenalised<=0 (doSound = 2). The resason I have them set to 1 and 2 is at one stage I played two different tones depending on the event (now I just play the same tone).

The two inputs to the tone playing are freq and length in ms.

Michael