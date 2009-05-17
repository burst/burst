//
// Copyright 2002,2003 Sony Corporation 
//
// Permission to use, copy, modify, and redistribute this software for
// non-commercial use is hereby granted.
//
// This software is provided "as is" without warranty of any kind,
// either expressed or implied, including but not limited to the
// implied warranties of fitness for a particular purpose.
//

#include <fstream>
#include <string.h>
#include <ant.h>
#include <OPENR/OSyslog.h>
#include <OPENR/OPENRAPI.h>
#include <OPENR/ODataFormats.h>
#include <OPENR/core_macro.h>
#include <EndpointTypes.h>
#include <UDPEndpointMsg.h>
#include <math.h>
#include "GameController.h"
#include "entry.h"
#include "RoboCupGameControlData.h"


bool DEBUG = false;


/* class constructor */ 
GameController::GameController() {
    for (int i = 0; i < NUM_LEDS; i++) ledID[i] = oprimitiveID_UNDEF;
    for (int i = 0; i < NUM_COMMAND_VECTOR; i++) region[i] = 0;
    for (int i = 0; i < NUM_ERS7_SENSORS; i++) {
        buttonCount[i] = 0;
        buttonPressed[i] = false;
    }
}


OStatus GameController::DoInit(const OSystemEvent &) {
    OSYSDEBUG(("GameController::DoInit()\n"));

    loadTeamCfg();
    initGameData();
    
    ipstackRef = antStackRef(strdup("IPStack"));

    /* initialise UDP buffers */
    for (int index = 0; index < GAMECONTROLLER_CONNECTION_MAX; index++) {
        OStatus result = InitUDPBuffer(index);
        if (result != oSUCCESS) return oFAIL;
    }

    /* initialise sensors */
    for (int i = 0; i < NUM_ERS7_SENSORS; i++) ers7idx[i] = -1;
    
    NEW_ALL_SUBJECT_AND_OBSERVER;
    REGISTER_ALL_ENTRY;
    SET_ALL_READY_AND_NOTIFY_ENTRY;
    OpenPrimitives();
    NewCommandVectorData();
    OPENR::SetMotorPower(opowerON);   
    
    return oSUCCESS;
}


OStatus GameController::DoStart(const OSystemEvent &) {
    OStatus result;
    OSYSDEBUG(("GameController::DoStart()\n"));

    for (int index = 0; index < GAMECONTROLLER_CONNECTION_MAX; index++) {
        // Bind and Start receive data
        result = CreateUDPEndpoint(index);
        if (result != oSUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s[%d]",
                  "GameController::DoStart()",
                  "CreateUDPEndpoint() fail", index));
            continue;
        }
        result = Bind(index);
        if (result != oSUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s[%d]",
                  "GameController::DoStart()",
                  "Bind() fail", index));
            continue;
        }
    }
    
    ENABLE_ALL_SUBJECT;
    ASSERT_READY_TO_ALL_OBSERVER; 
    
    OPowerStatus observationStatus;
    observationStatus.Set(orsbALL,
                          obsbALL,
                          opsoREMAINING_CAPACITY_NOTIFY_EVERY_CHANGE,
                          opsoTEMPERATURE_NOT_NOTIFY,
                          opsoTIME_DIF_NOT_NOTIFY,
                          opsoVOLUME_NOT_NOTIFY);
    
    OServiceEntry entry(myOID_, Extra_Entry[entryUpdatePowerStatus]);
    result = OPENR::ObservePowerStatus(observationStatus, entry);
    if(result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "GameController::DoStart()",
                  "OPENR::ObservePowerStatus() FAILED", result));
        return oFAIL;
    }    
        
    /* send first packet and turn on LEDs for the first time */
    notifyDataObservers();
    LEDUpdate();
    
    return oSUCCESS;
}  


OStatus GameController::DoStop(const OSystemEvent &) {
    OSYSDEBUG(("GameController::DoStop()\n"));

    for (int index = 0; index < GAMECONTROLLER_CONNECTION_MAX; index++) {
        if (connection[index].state != CONNECTION_CLOSED &&
            connection[index].state != CONNECTION_CLOSING) {

            // Connection close
            UDPEndpointCloseMsg closeMsg(connection[index].endpoint);
            closeMsg.Call(ipstackRef, sizeof(closeMsg));
            connection[index].state = CONNECTION_CLOSED;
        }
    }
    
    DISABLE_ALL_SUBJECT;
    DEASSERT_READY_TO_ALL_OBSERVER;    

    return oSUCCESS;
}


OStatus GameController::DoDestroy(const OSystemEvent &) {
    for (int index = 0; index < GAMECONTROLLER_CONNECTION_MAX; index++) {
        // UnMap and Destroy RecvBuffer
        connection[index].recvBuffer.UnMap();
        antEnvDestroySharedBufferMsg destroyRecvBufferMsg(connection[index].recvBuffer);
        destroyRecvBufferMsg.Call(ipstackRef, sizeof(destroyRecvBufferMsg));
    }

    DELETE_ALL_SUBJECT_AND_OBSERVER;
    
    return oSUCCESS;
}


/* this function loads the team & player number from team.cfg */
void GameController::loadTeamCfg() {
    
	const char *filename = GAMECONTROLLER_TEAM_CFG;
	std::ifstream in(filename);
     
    if (DEBUG) std::cerr << endl << "trying to load team.cfg...";
    
	if (in) {
		in >> teamNumber >> playerNumber;
        if (DEBUG) std::cerr << "I am player number " << playerNumber << " on team " << teamNumber << endl;
	}   
    
}

/* create the default RoboCupGameControlData, defaulting to blue team */
void GameController::initGameData() {
    
    memcpy(controlData.header, GAMECONTROLLER_STRUCT_HEADER, sizeof(controlData.header));
    controlData.version       = GAMECONTROLLER_STRUCT_VERSION;

    controlData.playersPerTeam = 4;
    if (playerNumber > 4)
    	controlData.playersPerTeam = playerNumber;

    controlData.state         = STATE_INITIAL;
    controlData.firstHalf     = 1;
    controlData.kickOffTeam   = TEAM_BLUE;
    controlData.secondaryState= STATE2_NORMAL;
    controlData.dropInTeam    = 0;
    controlData.dropInTime    = (uint16)-1;
    controlData.secsRemaining = 0;
    
    TeamInfo* blueTeam = &(controlData.teams[TEAM_BLUE]);
    TeamInfo* redTeam  = &(controlData.teams[TEAM_RED]);
    
    blueTeam->teamColour = TEAM_BLUE;
    blueTeam->teamNumber = teamNumber;
    blueTeam->score      = 0;    
    redTeam->teamColour  = TEAM_RED;
    redTeam->teamNumber  = (uint8)-1;        // undefined team
    redTeam->score       = 0;    
    
    for (int team=0; team<1; team++) {
        for (int player=0; player<MAX_NUM_PLAYERS; player++) {
            controlData.teams[team].players[player].penalty = PENALTY_NONE;
            controlData.teams[team].players[player].secsTillUnpenalised = 0;
        }
    }
    
    myTeam = blueTeam;
    
}    


/* notifies observers that the data structure has changed */
void GameController::notifyDataObservers() {
    subject[sbjTriggerData]->ClearBuffer();
    subject[sbjTriggerData]->SetData(&playerNumber, sizeof(playerNumber));
    subject[sbjTriggerData]->SetData(&teamNumber, sizeof(teamNumber));    
    subject[sbjTriggerData]->SetData(&controlData, sizeof(controlData));
    subject[sbjTriggerData]->NotifyObservers();    
}


/* interface function that returns the team that should next kick off */
uint32 GameController::getKickOffTeam() {
    return controlData.kickOffTeam;
}

/* return the current player number */
int GameController::getPlayerNumber() {
    return playerNumber;   
}

/* return the team number */
int GameController::getTeamNumber() {
    return myTeam->teamNumber;
}

/* return my team */
TeamInfo* GameController::getMyTeam() {
    return myTeam;
}

/* return the game control data "on demand" */
RoboCupGameControlData* GameController::getGameData() {
    return &controlData;
}


/* swap the teams in memory to maintain BLUE team first order */
void GameController::rawSwapTeams(RoboCupGameControlData* data) {
    size_t    teamSize = sizeof(TeamInfo);
    TeamInfo* blueTeam = &(data->teams[TEAM_BLUE]);
    TeamInfo* redTeam  = &(data->teams[TEAM_RED]);
    
    TeamInfo tempTeam;
    memcpy(&tempTeam, blueTeam, teamSize);    
    
    /* swap the teams */
    memcpy(blueTeam, redTeam, teamSize);
    memcpy(redTeam, &tempTeam, teamSize);
}


/* changes the current team to the new specified team colour */
void GameController::swapTeams(int team) {    
        
    /* don't swap unnecessarily */
    if ((uint32)team == myTeam->teamColour) return;

    rawSwapTeams(&controlData);
    
    /* adjust myTeam */
    if (team == TEAM_BLUE) {
        myTeam = &(controlData.teams[TEAM_BLUE]);
    } else {
        myTeam = &(controlData.teams[TEAM_RED]);
    }   

    /* don't change the team colours */    
    controlData.teams[TEAM_BLUE].teamColour = TEAM_BLUE;
    controlData.teams[TEAM_RED].teamColour  = TEAM_RED;
    
    if (DEBUG) std::cerr << "Swapped teams" << endl;
    
}



/******************************************************************************/
/* Code below is power related */
/******************************************************************************/

void GameController::UpdatePowerStatus(void *) {
    LEDUpdate();
}

void GameController::setPowerLED(RCRegion* rgn) {
    
    OPowerStatus power;
    OStatus result = OPENR::GetPowerStatus(&power);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "GameController::setPowerLED()",
                  "OPENR::GetPowerStatus() FAILED", result));
    }    
       
    OCommandVectorData* cmdVecData = (OCommandVectorData*)rgn->Base();    
    for (int i=0; i<NUM_LEDS; i++) {        
        OCommandData* data = cmdVecData->GetData(i);
        OLEDCommandValue3* value = (OLEDCommandValue3*)data->value;        
        if (correctPowerLED(power.remainingCapacity, i)) {
            for (int j=0; j<(int)ocommandMAX_FRAMES; j++) {
                value[j].intensity = LED_ON;
            }
        }
    }       
         
}


/* decides which LEDs should be turned on based on power remaining */
bool GameController::correctPowerLED(int remaining, int LED) {
    
    // battery is low
    if (remaining<GAMECONTROLLER_BATTERY_WARNING && LED==18) return true;   
    return false;
    
}



/******************************************************************************/
/* Code below is sensors related */
/******************************************************************************/  

/* callback function for the sensors */
void GameController::SensorUpdate(const ONotifyEvent& event) {
    
    //OSensorFrameVectorData* sensorVec = reinterpret_cast <OSensorFrameVectorData*>(event.Data(0));
	OSensorFrameVectorData *sensorVec = reinterpret_cast <OSensorFrameVectorData*>(event.RCData(0)->Base());
    
    if (initSensorIndex == false) {
        InitERS7SensorIndex(sensorVec);
        initSensorIndex = true;
    }
        
    processSensors(sensorVec);          // find out what was pressed...
    updateGameState();                  // ...and then act on them
    observer[event.ObsIndex()]->AssertReady();    
}


/* update the game state based on the current game state after a button press */
void GameController::updateGameState() {
    
    bool changes = false;           // flags whether buttons caused any changes
             
    /* check for game state change, which is done by the head button */
    if (buttonPressed[HEAD_SENSOR]) {
        
        /* if the robot is penalised and game is playing, unpenalise it */
        if (myTeam->players[playerNumber-1].penalty != PENALTY_NONE && 
            controlData.state == STATE_PLAYING) {
            /* need to hold for 3 seconds for reset to INITIAL or
               need to hold for 1 second for reset to PLAYING 
               this is processed in processSensors*/                           

        } else {

            changes = true;    
            
            /* otherwise change the game state normally */
            resetButton(HEAD_SENSOR);
            switch (controlData.state) {
            case STATE_INITIAL:        
                controlData.state = STATE_READY; 
                if (DEBUG) std::cerr << "Manual move from INITIAL to READY state" << endl;                
                break;
            case STATE_READY:             
                controlData.state = STATE_SET;
                if (DEBUG) std::cerr << "Manual move from READY to SET state" << endl;
                break;
            case STATE_SET:
                controlData.state = STATE_PLAYING;
                if (DEBUG) std::cerr << "Manual move from SET to PLAYING state" << endl;
                break;
            case STATE_PLAYING:
                // the rules do not allow PLAYING to go to FINISHED manually
                break;
            case STATE_FINISHED:
                // the rules do not allow this state to be reached manually
                break;
            }  
            holdCount = 0;
        }
    }

    /* check for team change or penalty in back buttons */
    if (buttonPressed[BACK_SW_F]) {                 
        changes = true;        
        resetButton(BACK_SW_F);
        
        switch (controlData.state) {            
        case STATE_INITIAL:              // selected blue team
            swapTeams(TEAM_BLUE);
            controlData.kickOffTeam = controlData.kickOffTeam ^ 1;
            break;     
            
        case STATE_PLAYING:              // go into penalty
            manualPenalise(true); break;
        }
    }
        
    /* check for team change or penalty in back buttons */
    if (buttonPressed[BACK_SW_R]) {      
        changes = true;
        resetButton(BACK_SW_R);
        
        switch (controlData.state) {     // selected red team
        case STATE_INITIAL:
            swapTeams(TEAM_RED);
            controlData.kickOffTeam = controlData.kickOffTeam ^ 1;
            break;            
        case STATE_PLAYING:              // go into penalty
            manualPenalise(true); break;
        }
    }
    
    /* check for kick off team change or penalty in back buttons */
    if (buttonPressed[BACK_SW_M]) {
        changes = true;
        resetButton(BACK_SW_M);
        
        switch (controlData.state) {
        case STATE_INITIAL:        
            if (controlData.kickOffTeam == TEAM_BLUE) {
                controlData.kickOffTeam = TEAM_RED;
                if (DEBUG) std::cerr << "Manual change to RED KICKOFF" << endl;
            } else {
                controlData.kickOffTeam = TEAM_BLUE;
                if (DEBUG) std::cerr << "Manual change to BLUE KICKOFF" << endl;
            }
            break;
            
        case STATE_PLAYING:              // go into penalty
            manualPenalise(true); break;
        }
    }
             
    /* notify observers if data has changed */
    if (changes) {
        notifyDataObservers();
        LEDUpdate();
        if (DEBUG) processGameData(&controlData);
    }
    
}


/* apply manual penalise to the robot.  The bool allows
 * both penalise and unpenalise in this function. */
void GameController::manualPenalise(bool penalise) {
    myTeam->players[playerNumber-1].penalty = penalise?PENALTY_MANUAL:PENALTY_NONE;
    if (DEBUG) std::cerr << "Manual PENALISE: " << penalise << endl;
    
    //
    // Broadcast a message so the GameContoller knows we're penalised
    //

    RoboCupGameControlReturnData returnPacket;
    
    memcpy(returnPacket.header, GAMECONTROLLER_RETURN_STRUCT_HEADER, sizeof(returnPacket.header));
    returnPacket.version = GAMECONTROLLER_RETURN_STRUCT_VERSION;
    returnPacket.team = teamNumber;
    returnPacket.player = playerNumber;
    returnPacket.message = penalise?GAMECONTROLLER_RETURN_MSG_MAN_PENALISE:
                                    GAMECONTROLLER_RETURN_MSG_MAN_UNPENALISE;
    
    int index = 0;
    
    if (connection[index].state != CONNECTION_CONNECTED)	// don't overwrite a current packet
    	return;
    
    connection[index].sendAddress = IP_ADDR_BROADCAST;
    connection[index].sendPort    = GAMECONTROLLER_PORT;
    connection[index].sendSize    = sizeof(RoboCupGameControlReturnData);
    memcpy(connection[index].sendData, &returnPacket, sizeof(RoboCupGameControlReturnData));

    Send(index);
}


/* turns a button "off" and forces it to be released first */
void GameController::resetButton(int button) {
    buttonPressed[button] = false;
    buttonCount[button] = -1;           // -1 signifies a release is required
}


/* print out the sensor values for the back and head buttons */
void GameController::processSensors(OSensorFrameVectorData* sensorVec) {
    
    int value     = 0;
    int threshold = 0;
        
    for (int i=0; i<NUM_ERS7_SENSORS; i++) {
        value = getSensorValue(sensorVec, ers7idx[i]);
        
        /* adjust the button pressure threshold for different buttons */
        if (i == HEAD_SENSOR) {
            threshold = HEAD_THRESHOLD;
        } else {
            threshold = BACK_THRESHOLD;
        }        
        
        /* check if the button needs a release before it can be used */
        if (buttonCount[i] == -1) {        
            if (value < threshold) buttonCount[i] = 0;

        /* increase count of the button press if greater than the threshold */            
        } else {
            
            int triggerCount;
            
            /* to allow for 100ms for head sensor, but 1000ms for back sensors */
            if (i == HEAD_SENSOR || controlData.state != STATE_PLAYING) {
                triggerCount = SENSOR_TRIGGER_TIME/SENSOR_UPDATES;
            } else {
                triggerCount = PENALTY_TRIGGER_TIME/SENSOR_UPDATES;
            }
            
            if (value > threshold) {
                buttonCount[i]++;
                if (buttonCount[i] >= triggerCount) {
                    buttonCount[i]   = 0;
                    buttonPressed[i] = true;
                    if (i == HEAD_SENSOR) {
                        holdCount++;
                        if (DEBUG) std::cerr << "head held for " << holdCount << "*" << SENSOR_TRIGGER_TIME << "ms" << endl;
                    }
                }
            } else {                            // button released, reset count
                              
                /* detect the release of the head button for unpenalising here */
                if (buttonPressed[HEAD_SENSOR]) {
                    if (myTeam->players[playerNumber-1].penalty != PENALTY_NONE &&
                        controlData.state == STATE_PLAYING &&
                        i == HEAD_SENSOR) {
                                    
                        resetButton(HEAD_SENSOR);
			manualPenalise(false);
                        
                        /* reset to initial if head for more than 3 secs */
                        if (holdCount >= UNPENALISE_HOLDTIME_INITIAL) {
                            controlData.state = STATE_INITIAL;
                            if (DEBUG) std::cerr << "Manual UNPENALISE to INITIAL" << endl;
                            LEDUpdate();
                            notifyDataObservers();
                        } else {
                            controlData.state = STATE_PLAYING;
                            LEDUpdate();
                            notifyDataObservers();
                            if (DEBUG) std::cerr << "Manual UNPENALISE to PLAYING" << endl;
                        }
                        holdCount   = 0;
                    }        
                }
                buttonCount[i]   = 0;
                buttonPressed[i] = false;     
            }
        }
    }

}


/* prints out frame 0 in sensor data */ 
int GameController::getSensorValue(OSensorFrameVectorData* sensorVec, int index) {
    OSensorFrameData* data = sensorVec->GetData(index);    
    return data->frame[0].value;    
}


/* creates an array of OSensorFrameVectorData that I imagine allows the program
   to access each sensor specified in ERS7_SENSOR_LOCATOR */
void GameController::InitERS7SensorIndex(OSensorFrameVectorData* sensorVec) {
    OStatus result;
    OPrimitiveID sensorID;
    
    for (int i = 0; i < NUM_ERS7_SENSORS; i++) {

        result = OPENR::OpenPrimitive(ERS7_SENSOR_LOCATOR[i], &sensorID);
        if (result != oSUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s %d",
                      "SensorObserver7::InitERS7SensorIndex()",
                      "OPENR::OpenPrimitive() FAILED", result));
            continue;
        }

        for (int j = 0; j < (int)(sensorVec->vectorInfo.numData); j++) {
            OSensorFrameInfo* info = sensorVec->GetInfo(j);
            if (info->primitiveID == sensorID) {
                ers7idx[i] = j;
                OSYSPRINT(("[%2d] %s\n", ers7idx[i], ERS7_SENSOR_LOCATOR[i]));
                break;
            }
        }
    }
}

void GameController::beepOnUnfairPenalize(RoboCupGameControlData* gameData) {
	TeamInfo* tm;
	
	if (gameData->teams[TEAM_BLUE].teamNumber == teamNumber) {
		tm = &(gameData->teams[TEAM_BLUE]);
	} else if (gameData->teams[TEAM_RED].teamNumber == teamNumber){
		tm = &(gameData->teams[TEAM_RED]);
	} else {
		return;
	}
	
	if ((tm->players[playerNumber-1].penalty != PENALTY_NONE) &&
			(tm->players[playerNumber-1].secsTillUnpenalised == 0)) {
        if (subject[sbjSoundCommand]->IsAnyReady()) {	// should still work even if they don't use the sound object
            const char* SoundCommand = "525 400";
            subject[sbjSoundCommand]->ClearBuffer();
            subject[sbjSoundCommand]->SetData(SoundCommand, strlen(SoundCommand)+1);
            subject[sbjSoundCommand]->NotifyObservers();
        }
	}
}

/******************************************************************************/
/* Code below is UDP related */
/******************************************************************************/

/* UDP messages come through here */
void GameController::ReceiveCont(ANTENVMSG msg) {
	
    UDPEndpointReceiveMsg* receiveMsg = (UDPEndpointReceiveMsg*)antEnvMsg::Receive(msg);

    int index = (int)(receiveMsg->continuation);
    if (connection[index].state == CONNECTION_CLOSED) return;

    if (receiveMsg->error != UDP_SUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "GameController::ReceiveCont()",
                  "FAILED. receiveMsg->error", receiveMsg->error));
        Close(index);
        return;
    }
        
    
    /* get a data structure out of the byte stream */    
    RoboCupGameControlData* tempData = (RoboCupGameControlData*)(receiveMsg->buffer);

    /* process only if the packet is good */    
    if (validatePacket(tempData)) {
        
        /* Normalise the team structure order so that BLUE is always first */
        if (tempData->teams[TEAM_BLUE].teamColour != TEAM_BLUE)
            rawSwapTeams(tempData);
        
        /* Beep if we just got a wireless command that has us penalized with remaining time 0 */
        beepOnUnfairPenalize(tempData);
        
        /* print it out if this packet is different to the previous one
           and is relevant to this game */
        if (!dataEqual(tempData, &controlData)) {
            memcpy(&controlData, tempData, sizeof(RoboCupGameControlData));
            
            /* make myTeam point to the my actual team, based on teamNumber */        
            if (controlData.teams[TEAM_BLUE].teamNumber == teamNumber) {
                myTeam = &controlData.teams[TEAM_BLUE];
            } else if (controlData.teams[TEAM_RED].teamNumber == teamNumber) {
                myTeam = &controlData.teams[TEAM_RED];
            }
            
            notifyDataObservers();
            LEDUpdate();
            if (DEBUG) {
                std::cerr << "UDP update" << endl;
                processGameData(&controlData);
            }
        }      
    }
                
    /* get ready for another receive */    
    connection[index].state    = CONNECTION_CONNECTED;
    connection[index].recvSize = GAMECONTROLLER_BUFFER_SIZE;
    Receive(index);
    
}


/* runs various checks and returns true/false for good/bad packet */
bool GameController::validatePacket(RoboCupGameControlData *data) {
        
    /* check the right structure header has come in */
    if (!(checkHeader(data->header))) {
        OSYSPRINT(("DATA HEADER MISMATCH\n"));
        OSYSPRINT(("local header is %s, received header is %s", 
                    GAMECONTROLLER_STRUCT_HEADER, data->header));      
        return false;
    }
    
    /* check for partial packets */
    if (sizeof(*data) != sizeof(RoboCupGameControlData)) {
        OSYSPRINT(("RECEIVED PARTIAL PACKET\n"));
        std::cerr << "data: " << sizeof(*data) << " " << "controller: " << sizeof(RoboCupGameControlData) << endl;
        return false;
    }    
        
    /* check the right version of the structure is being used */
    if (data->version != GAMECONTROLLER_STRUCT_VERSION) {
        OSYSPRINT(("DATA VERSION MISMATCH\n"));
        OSYSPRINT(("local version is version %d, receiving version %d", 
                    GAMECONTROLLER_STRUCT_VERSION, data->version));
        return false;                 
    }   

    /* check whether this packet belongs to this game at all */
    if (!isThisGame(data)) return false;
     
    return true;
}


/* checks the header of a packet. Since the GameController broadcasts 4 
   characters and not a string (which is terminated by a \0), we should check
   each character individually instead of using something like strcmp */
bool GameController::checkHeader(char* header) {
    for (int i=0; i<4; i++)
        if (header[i] != GAMECONTROLLER_STRUCT_HEADER[i]) return false;
    return true;    
}


/* compare two byte streams, returns true (match) or false (no match) */
bool GameController::dataEqual(void* data, void* previous) {
    if (!memcmp(previous, data, sizeof(RoboCupGameControlData)))
        return true;
    return false;
}


/* checks whether a packet even belongs in this game */
bool GameController::isThisGame(RoboCupGameControlData* gameData) {
 
    if (gameData->teams[TEAM_BLUE].teamNumber != teamNumber &&
        gameData->teams[TEAM_RED].teamNumber  != teamNumber) {
        if (DEBUG) std::cerr << "Got packet not for this game" << endl;
        return false;
    }   
    return true;
            
}


/* given a RoboGameControlData and print out for debug */
void GameController::processGameData(RoboCupGameControlData* gameData) {
    
    if (DEBUG) std::cerr << "GameController (v" << gameData->version << "): ";

    /* check whether this packet belongs to this game 
       and set myTeam to point to my team's TeamInfo */
    if (gameData->teams[TEAM_BLUE].teamNumber == myTeam->teamNumber) {
        if (DEBUG) std::cerr << "BLUE team (score " << myTeam->score << "), ";

    } else if (gameData->teams[TEAM_RED].teamNumber == myTeam->teamNumber) {
        if (DEBUG) std::cerr << "RED team (score " << myTeam->score << "), ";
        
    } else {

        // packets that don't belong in this game should have already been
        // filtered by isThisGame
        return;
    }
    
    /* check which half the game is in */
    if (gameData->firstHalf == 1) { 
        if (DEBUG) std::cerr << "1st half ";
    } else {
        if (DEBUG) std::cerr << "2nd half ";
    }
    
    /* check what state the game is in */
    if (gameData->state == STATE_INITIAL) {
        if (DEBUG) std::cerr << "(INITIAL) ";
    } else if (gameData->state == STATE_READY) {
        if (DEBUG) std::cerr << "(READY) ";
    } else if (gameData->state == STATE_SET) {
        if (DEBUG) std::cerr << "(SET) ";
    } else if (gameData->state == STATE_PLAYING) {
        if (DEBUG) std::cerr << "(PLAYING) ";
    } else if (gameData->state == STATE_FINISHED) {
        if (DEBUG) std::cerr << "(FINISHED) ";
    }
        
    /* look at who is kicking off */
    if (gameData->kickOffTeam == myTeam->teamColour) {
        if (DEBUG) std::cerr << "OWN kickoff, ";
    } else {
        if (DEBUG) std::cerr << "OTHER kickoff, ";
    }    
    
    /* Is it a penalty shootout? */
    if (gameData->secondaryState != STATE2_NORMAL) {
        if (DEBUG) std::cerr << "Secondary state: "
                << gameData->secondaryState << ", ";
    }
    
    /* look at my penalty */
    if (myTeam->players[playerNumber-1].penalty == PENALTY_NONE) {
        if (DEBUG) std::cerr << "I am NOT PENALISED, ";
    } else {
        switch (myTeam->players[playerNumber-1].penalty) {
        case PENALTY_BALL_HOLDING:
            if (DEBUG) std::cerr << "PENALTY_BALL_HOLDING for ";
            break;
        case PENALTY_GOALIE_PUSHING:
            if (DEBUG) std::cerr << "PENALTY_GOALIE_PUSHING for ";
            break;
        case PENALTY_PLAYER_PUSHING:
            if (DEBUG) std::cerr << "PENALTY_PLAYER_PUSHING for ";
            break;
        case PENALTY_ILLEGAL_DEFENDER:
            if (DEBUG) std::cerr << "PENALTY_ILLEGAL_DEFENDER for ";
            break;
        case PENALTY_ILLEGAL_DEFENSE:
            if (DEBUG) std::cerr << "PENALTY_ILLEGAL_DEFENSE for ";
            break;
        case PENALTY_OBSTRUCTION:
            if (DEBUG) std::cerr << "PENALTY_OBSTRUCTION for ";
            break;
        case PENALTY_REQ_FOR_PICKUP:
            if (DEBUG) std::cerr << "PENALTY_REQ_FOR_PICKUP for ";
            break;
        case PENALTY_LEAVING:
            if (DEBUG) std::cerr << "PENALTY_LEAVING for ";
            break;
        case PENALTY_DAMAGE:
            if (DEBUG) std::cerr << "PENALTY_DAMAGE for ";
            break;
        case PENALTY_MANUAL:
            if (DEBUG) std::cerr << "PENALTY_MANUAL for ";
            break;
        default:
            if (DEBUG) std::cerr << "Unknown penalty for ";
            break;
        }
        if (DEBUG) std::cerr << myTeam->players[playerNumber-1].secsTillUnpenalised << " secs, ";
    }
    
    /* look at remaining time */
    if (DEBUG) std::cerr << gameData->secsRemaining << " secs remaining" << endl;
        
    /*
    gameData->dropInTeam, 
    gameData->dropInTime));
    */
}


OStatus
GameController::Send(int index)
{
    OSYSDEBUG(("GameController::Send()\n"));

    if (connection[index].sendSize == 0 ||
        connection[index].state != CONNECTION_CONNECTED) return oFAIL;

    UDPEndpointSendMsg sendMsg(connection[index].endpoint,
                               connection[index].sendAddress,
                               connection[index].sendPort,
                               connection[index].sendData,
                               connection[index].sendSize);
    sendMsg.continuation = (void*)index;
    sendMsg.Send(ipstackRef, myOID_,
                 Extra_Entry[entrySendCont], sizeof(UDPEndpointSendMsg));
                 

    connection[index].state = CONNECTION_SENDING;
    return oSUCCESS;
}

void
GameController::SendCont(ANTENVMSG msg)
{
    OSYSDEBUG(("GameController::SendCont()\n"));

    UDPEndpointSendMsg* sendMsg = (UDPEndpointSendMsg*)antEnvMsg::Receive(msg);
    int index = (int)(sendMsg->continuation);
    if (connection[index].state == CONNECTION_CLOSED)
        return;

    if (sendMsg->error != UDP_SUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s %d",
                  "GameController::SendCont()",
                  "FAILED. sendMsg->error", sendMsg->error));
        Close(index);
        return;
    }

    connection[index].state = CONNECTION_CONNECTED;
}

OStatus GameController::Receive(int index) {

    if (connection[index].state != CONNECTION_CONNECTED &&
        connection[index].state != CONNECTION_SENDING) return oFAIL;

    UDPEndpointReceiveMsg receiveMsg(connection[index].endpoint,
                                     connection[index].recvData,
                                     connection[index].recvSize);
    receiveMsg.continuation = (void*)index;

    receiveMsg.Send(ipstackRef, myOID_,
                    Extra_Entry[entryReceiveCont], sizeof(receiveMsg));

    return oSUCCESS;
}


OStatus GameController::Close(int index) {
    OSYSDEBUG(("GameController::Close()\n"));

    if (connection[index].state == CONNECTION_CLOSED ||
        connection[index].state == CONNECTION_CLOSING) return oFAIL;

    UDPEndpointCloseMsg closeMsg(connection[index].endpoint);
    closeMsg.continuation = (void*)index;

    closeMsg.Send(ipstackRef, myOID_,
                  Extra_Entry[entryCloseCont], sizeof(closeMsg));

    connection[index].state = CONNECTION_CLOSING;

    return oSUCCESS;
}


void GameController::CloseCont(ANTENVMSG msg) {
    OStatus result;
    OSYSDEBUG(("GameController::CloseCont()\n"));
    
    UDPEndpointCloseMsg* closeMsg = (UDPEndpointCloseMsg*)antEnvMsg::Receive(msg);
    int index = (int)(closeMsg->continuation);
    if (connection[index].state == CONNECTION_CLOSED)
        return;

    connection[index].state = CONNECTION_CLOSED;

    result = CreateUDPEndpoint(index);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s[%d]",
                  "GameController::CloseCont()",
                  "CreateUDPEndpoint() fail", index));
        return;
    }
    result = Bind(index);
    if (result != oSUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s[%d]",
                  "GameController::CloseCont()",
                  "Bind() fail", index));
    }
}


OStatus GameController::InitUDPBuffer(int index) {
    OSYSDEBUG(("GameController::InitUDPBuffer()\n"));

    connection[index].state = CONNECTION_CLOSED;

    // Allocate send buffer
    antEnvCreateSharedBufferMsg sendBufferMsg(GAMECONTROLLER_RETURN_BUFFER_SIZE);

    sendBufferMsg.Call(ipstackRef, sizeof(sendBufferMsg));
    if (sendBufferMsg.error != ANT_SUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s[%d] antError %d",
                  "GameController::InitUDPBuffer()",
                  "Can't allocate send buffer",
                  index, sendBufferMsg.error));
        return oFAIL;
    }
	
    connection[index].sendBuffer = sendBufferMsg.buffer;
    connection[index].sendBuffer.Map();
    connection[index].sendData
        = (byte*)(connection[index].sendBuffer.GetAddress());

    // Allocate receive buffer
    antEnvCreateSharedBufferMsg recvBufferMsg(GAMECONTROLLER_BUFFER_SIZE);

    recvBufferMsg.Call(ipstackRef, sizeof(recvBufferMsg));
    if (recvBufferMsg.error != ANT_SUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s[%d] antError %d",
                  "GameController::InitUDPBuffer()",
                  "Can't allocate receive buffer",
                  index, recvBufferMsg.error));
        return oFAIL;
    }

    connection[index].recvBuffer = recvBufferMsg.buffer;
    connection[index].recvBuffer.Map();
    connection[index].recvData
        = (byte*)(connection[index].recvBuffer.GetAddress());
    connection[index].recvSize = GAMECONTROLLER_BUFFER_SIZE;

    return oSUCCESS;
}


OStatus GameController::CreateUDPEndpoint(int index) {
    OSYSDEBUG(("GameController::CreateUDPEndpoint()\n"));

    if (connection[index].state != CONNECTION_CLOSED) return oFAIL;

    // Create UDP endpoint
    antEnvCreateEndpointMsg udpCreateMsg(EndpointType_UDP,
                                         GAMECONTROLLER_BUFFER_SIZE * 2);
    udpCreateMsg.Call(ipstackRef, sizeof(udpCreateMsg));
    if (udpCreateMsg.error != ANT_SUCCESS) {
        OSYSLOG1((osyslogERROR, "%s : %s[%d] antError %d",
                  "GameController::CreateUDPEndpoint()",
                  "Can't create endpoint",
                  index, udpCreateMsg.error));
        return oFAIL;
    }
    connection[index].endpoint = udpCreateMsg.moduleRef;

    return oSUCCESS;
}


OStatus GameController::Bind(int index) {
    
    OSYSDEBUG(("GameController::Bind()\n"));

    if (connection[index].state != CONNECTION_CLOSED) return oFAIL;

    // Bind
    UDPEndpointBindMsg bindMsg(connection[index].endpoint, 
                               IP_ADDR_ANY, GAMECONTROLLER_PORT);
    bindMsg.Call(ipstackRef,sizeof(antEnvCreateEndpointMsg));
    if (bindMsg.error != UDP_SUCCESS) {
        return oFAIL;
    }

    connection[index].state = CONNECTION_CONNECTED;
    connection[index].recvSize = GAMECONTROLLER_BUFFER_SIZE;

    Receive(index);

    return oSUCCESS;
}



/******************************************************************************/
/* Code below is LED related */
/******************************************************************************/

/* update the LEDs based on the data structure */
void GameController::LEDUpdate() {
    // GameController shouldn't affect LEDs during game
    // only during INITIAL, READY and SET
    if (controlData.state != STATE_INITIAL &&
        controlData.state != STATE_READY &&
        controlData.state != STATE_SET) return;
        
    RCRegion* rgn = FindFreeRegion();
    
    if (rgn == 0) {
        cout << "Unable to find free region while setting LEDs in GameController Object" << endl;
        return;
    }
    
    initLEDs(rgn);
    
    if (controlData.kickOffTeam == myTeam->teamColour)
        setBackLED(YELLOW_LED, rgn);
   
    if (myTeam->teamColour == TEAM_BLUE) {
        setBackLED(BLUE_LED, rgn);
    } else {
        setBackLED(RED_LED, rgn);        
    }
         
    setFaceLED(rgn);    
    setPowerLED(rgn);
    
    subject[sbjLED]->SetData(rgn);
    subject[sbjLED]->NotifyObservers();            
}  


/* turn all LEDs off */
void GameController::initLEDs(RCRegion* rgn) {    
    OCommandVectorData* cmdVecData = (OCommandVectorData*)rgn->Base();
    for (int i=0; i<NUM_LEDS; i++) {        
        OCommandData* data = cmdVecData->GetData(i);
        OLEDCommandValue3* val = (OLEDCommandValue3*)data->value;        
        for (int j=0; j<(int)ocommandMAX_FRAMES; j++) {
            val[j].intensity = LED_OFF;  
            val[j].mode      = oled3_MODE_A;
            val[j].period    = 1;
        }
    } 
}


/* turn on the face LEDs for the player number */
void GameController::setFaceLED(RCRegion* rgn) {    
    OCommandVectorData* cmdVecData = (OCommandVectorData*)rgn->Base();
    for (int i=0; i<NUM_LEDS; i++) {        
        OCommandData* data = cmdVecData->GetData(i);
        OLEDCommandValue3* value = (OLEDCommandValue3*)data->value;
        if (correctPlayerLED(playerNumber, i)) {        
            for (int j=0; j<(int)ocommandMAX_FRAMES; j++) {                
                value[j].intensity = LED_ON;                
            }
        }
    }
}


/* decides whether a LED should be on for a particular player
   see OPEN-R ERS7 model information for LED patterns 
   notice that there is an offset of 6 from what is in the SDK
   documentation since in LOCATOR the first 6 places have
   been used by the back LEDs*/
bool GameController::correctPlayerLED(int player, int LED) {
 
    if (player == 1 && LED != 17) {
        return false;      
    } else if (player == 2 && LED != 8 && LED != 9) {
        return false;        
    } else if (player == 3 && LED != 8 && LED != 9 && LED != 17) {
        return false;        
    } else if (player == 4 && LED != 6 && LED != 7 && LED != 12 && LED != 13) {
        return false;
    }
    
    return true;    
}


/* turns on/off the back LEDs */
void GameController::setBackLED(int LED, RCRegion* rgn) {
    OCommandVectorData* cmdVecData = (OCommandVectorData*)rgn->Base();    
    for (int i=0; i<NUM_LEDS; i++) {        
        OCommandData* wdata = cmdVecData->GetData(i);        
        OLEDCommandValue3* value = (OLEDCommandValue3*)wdata->value;        
        for (int j=0; j<(int)ocommandMAX_FRAMES; j++) {
            if (i == LED) value[j].intensity = LED_ON;
        }
    }
}    


RCRegion* GameController::FindFreeRegion(){ 
    for (int i = 0; i < NUM_COMMAND_VECTOR; i++) {
        if (region[i]->NumberOfReference() == 1) return region[i];
    }
    return 0;
}


void GameController::OpenPrimitives() { 
    for (int i = 0; i < NUM_LEDS; i++) {
        OStatus result = OPENR::OpenPrimitive(LOCATOR[i], &ledID[i]);
        if (result != oSUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s %d",
                      "GameController::OpenPrimitives()",
                      "OPENR::OpenPrimitive() FAILED", result));
        }
    }       
}
 

void GameController::NewCommandVectorData() {
    OStatus result;
    MemoryRegionID      cmdVecDataID;
    OCommandVectorData* cmdVecData;

    for (int i = 0; i < NUM_COMMAND_VECTOR; i++) {

        result = OPENR::NewCommandVectorData(NUM_LEDS, &cmdVecDataID, &cmdVecData);
        if (result != oSUCCESS) {
            OSYSLOG1((osyslogERROR, "%s : %s %d",
                      "GameController::NewCommandVectorData()",
                      "OPENR::NewCommandVectorData() FAILED", result));
        }

        region[i] = new RCRegion(cmdVecData->vectorInfo.memRegionID,
                                 cmdVecData->vectorInfo.offset,
                                 (void*)cmdVecData,
                                 cmdVecData->vectorInfo.totalSize);

        cmdVecData->SetNumData(NUM_LEDS);

        for (int j = 0; j < NUM_LEDS; j++) {
            OCommandInfo* info = cmdVecData->GetInfo(j);
            info->Set(odataLED_COMMAND3, ledID[j], ocommandMAX_FRAMES);
        }
    }  

    
}
