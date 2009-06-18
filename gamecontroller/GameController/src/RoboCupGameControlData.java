/*
    Copyright (C) 2005  University Of New South Wales

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

import java.nio.ByteBuffer;
/*
 * RoboCupGameControlData.java
 *
 * Created on 10 January 2005, 12:17
 */

/**
 * This class holds the RoboCupGameControl data structure. Refer to the readme
 * for more information of its structure. The class can convert itself into a 
 * little endian byte array for sending over a network
 * 
 * @author willu@cse.unsw.edu.au shnl327@cse.unsw.edu.au
 */


public class RoboCupGameControlData {
    
    
    // number of bytes for an int
    public static final int INT32_SIZE = 4;
    public static final int INT16_SIZE = 2;
    public static final int INT8_SIZE = 1;
    
    // data structure header string, keep this at 4 characters/bytes
    public static final String STRUCT_HEADER = "RGme";
    public static final int STRUCT_VERSION = 6;

    // RoboCupGameControlData has two TeamInfos in it, a red and a blue
    private TeamInfo[] teams = new TeamInfo[2];
    
    private byte playersPerTeam;
    private byte gameState;                                
    private byte firstHalf = (byte)Constants.TRUE;
    private byte kickOffTeam;
    private byte secondaryState;
    private byte dropInTeam;
    private short dropInTime = -1;        // -ve time = first dropin yet to happen   
    private boolean noDropInYet = true; // this will stop the timer from counting drop in time
    private int estimatedSecs;
    
	// size in bytes of the packet.  Note that the packet format was carefully
	// chosen to not require padding.  If you change the packet format, then
	// you may need to account for compiler padding of the structure.
    private static final int packet_size = (
		4 +					// header
		INT32_SIZE +		// version
		INT8_SIZE +			// playersPerTeam
		INT8_SIZE +			// state
		INT8_SIZE +			// firstHalf
		INT8_SIZE +			// kickOffTeam
		INT8_SIZE +			// secondaryState
		INT8_SIZE +			// dropInTeam
		INT16_SIZE +		// dropInTime
		INT32_SIZE +		// secsRemaining
		2*(
			INT8_SIZE +			// teamNumber
			INT8_SIZE +			// teamColour
			INT16_SIZE +		// score
			Constants.MAX_NUM_PLAYERS*(
				INT16_SIZE + 	// penalty
				INT16_SIZE	 	// secsTillUnpenalised
			)
		)
	);
    
    
    /** Creates a new instance of RoboCupGameControlData */
    public RoboCupGameControlData() {
    }
    
    public RoboCupGameControlData(byte blueNumber, byte redNumber, int playersPerTeam) {
        teams[0] = new TeamInfo(Constants.TEAM_BLUE, blueNumber, playersPerTeam);
        teams[1] = new TeamInfo(Constants.TEAM_RED, redNumber, playersPerTeam);
        estimatedSecs = 60*Constants.TIME_MINUTES;
        if ((playersPerTeam < 1) || (playersPerTeam > Constants.MAX_NUM_PLAYERS))
        	throw new RuntimeException("Bad number of players");
        this.playersPerTeam = (byte)playersPerTeam;
    }

        
    // get the object as a byte array
    // do this by converting the team's combined strings and field values and 
    // performing a getBytes on it
    public synchronized byte[] getAsByteArray() {
		
		ByteBuffer buffer = ByteBuffer.allocate(packet_size+10);
		buffer.order(Constants.PACKET_BYTEORDER);
		
		buffer.put(STRUCT_HEADER.getBytes());
		buffer.putInt(STRUCT_VERSION);
		
		buffer.put(playersPerTeam);
		buffer.put(gameState);
		buffer.put(firstHalf);
		buffer.put(kickOffTeam);
		buffer.put(secondaryState);
		buffer.put(dropInTeam);
		buffer.putShort(dropInTime);
		buffer.putInt(estimatedSecs);
		
		// blue team
		
		buffer.put((byte)getTeamNumber(Constants.TEAM_BLUE));
		buffer.put((byte)Constants.TEAM_BLUE);
		buffer.putShort((short)getScore(Constants.TEAM_BLUE));
		
		for (int i=0; i<Constants.MAX_NUM_PLAYERS; i++) {
			buffer.putShort((short)teams[Constants.TEAM_BLUE].getPlayers()[i].getPenalty());
			buffer.putShort((short)teams[Constants.TEAM_BLUE].getPlayers()[i].getSecsTillUnpenalised());
		}
		
		// red team
		
		buffer.put((byte)getTeamNumber(Constants.TEAM_RED));
		buffer.put((byte)Constants.TEAM_RED);
		buffer.putShort((short)getScore(Constants.TEAM_RED));
		
		for (int i=0; i<Constants.MAX_NUM_PLAYERS; i++) {
			buffer.putShort((short)teams[Constants.TEAM_RED].getPlayers()[i].getPenalty());
			buffer.putShort((short)teams[Constants.TEAM_RED].getPlayers()[i].getSecsTillUnpenalised());
		}
		
		buffer.rewind();
        byte[] array = new byte[packet_size];
        buffer.get(array);

        // print out the binary array and debug   
        if (Constants.debug) {
            
            String blueString = teams[0].toString();
            String redString  = teams[1].toString();
            String dataString = "Hr:" + STRUCT_HEADER + " " + 
                                "Vr:" + STRUCT_VERSION + " " + 
                                "St:" + gameState + " " + 
                                "1st:" + firstHalf + " " + 
                                "KOTeam:" + kickOffTeam + " " + 
                                "SecState:" + secondaryState + " " + 
                                "DropT:" + dropInTeam + " " +
                                "DropS:" + dropInTime + " " +                                
                                "Secs:" + estimatedSecs + " " +
                                "(" + blueString + ") (" + redString + ")";
        
            System.out.println(dataString);             
            
            for (int i=0; i<array.length; i++) {
                if (i%4==0) { System.out.print("|"); }
                String thisByte = Integer.toHexString(array[i]);
                if (thisByte.length() == 1) {
                	System.out.print("0");
                }
                System.out.print(thisByte);
            }
            System.out.println();        
        }
        
        return array;
    }
    
    
    public synchronized void setPlayersPerTeam(byte playersPerTeam) {
    	this.playersPerTeam = playersPerTeam;
    }
    
    public synchronized byte getPlayersPerTeam() {
    	return playersPerTeam;
    }
    
    // update the drop in times
    public synchronized void updateDropInTime() {
        if (!noDropInYet) {
        	dropInTime++;
        	if (dropInTime > 10*60) {
        		// make sure time doesn't wrap by reseting to no drop-in seen after 10 minutes
        		noDropInYet = true;
        		dropInTime = -1;
        	}
        }
    }
        
    // change the last team that was favoured
    public synchronized void setDropInTeam(byte team) {
        noDropInYet = false;
        this.dropInTeam = team;
        this.dropInTime = 0;        // reset counter on drop in change
    }
    
    // resets the drop in for a new half
    public synchronized void resetDropIn() {
        noDropInYet = true;
        this.dropInTeam = Constants.TEAM_BLUE;
        this.dropInTime = -1;
    }
    
    
    // resets all the penalties of the dogs for a new kick off, etc
    public synchronized void resetPenalties() {
        for (int x=0; x<2; x++) {
            for (int y=0; y<4; y++) {
                teams[x].getPlayers()[y].setPenalty(Constants.PENALTY_NONE);
            }
        }        
    }    
    
    
    // return the specified team (0 = blue, 1 = red)
    public synchronized TeamInfo getTeam(byte team) {
        return teams[team];
    }
            
    
    // make the data structure into a certain game state
    public synchronized void setGameState(byte gameState) {
        this.gameState = gameState;
    }    
    
    public synchronized byte getGameState() {
        return this.gameState;
    }       
       
    // make the data structure into a certain secondary game state
    public synchronized void setSecondaryGameState(byte secondaryState) {
        this.secondaryState = secondaryState;
    }    
    
    public synchronized byte getSecondaryGameState() {
        return this.secondaryState;
    }       
       
        
    // get the first half / second half flag
    public synchronized boolean getHalf() {
        return (firstHalf==Constants.TRUE);
    }
    
    // set the first half / second half flag
    public synchronized void setHalf(byte firstHalf) {
        this.firstHalf = firstHalf;
    }
    
    public synchronized void setHalf(int firstHalf) {
        this.firstHalf = (byte)firstHalf;
    }
    
    // set the first half / second half flag
    public synchronized void setHalf(boolean firstHalf) {
        setHalf(firstHalf?Constants.TRUE:Constants.FALSE);
    }
    
    
    // set the number of estimated seconds remaining in the half
    // the parameter comes from the clock label
    // return 0 seconds when in overtime
    public synchronized void setEstimatedSecs(int time, boolean overTime) {       
        if (overTime == false) {
            this.estimatedSecs = time;
        } else {
            this.estimatedSecs = 0;
        }
    }
     

    // get the kick off team
    public synchronized byte getKickOffTeam() {
        return kickOffTeam;
    }
    
    // set the kick off team
    public synchronized void setKickOffTeam(byte kickOffTeam) {
        this.kickOffTeam = kickOffTeam;
    }

    public synchronized void setKickOffTeam(int kickOffTeam) {
    	if ((kickOffTeam < 0) || (kickOffTeam > Byte.MAX_VALUE))
    		throw new RuntimeException("Bad Kickoff Team number");
        this.kickOffTeam = (byte)kickOffTeam;
    }
    
    
    // gets/sets team number
    public synchronized int getTeamNumber(byte team) {
        return teams[team].getTeamNumber();
    }
    
    public synchronized void setTeamNumber(byte team, byte number) {
        teams[team].setTeamNumber(number);
    }

    public synchronized void setTeamNumber(int team, int number) {
    	if ((number < 0) || (number > Byte.MAX_VALUE))
    		throw new RuntimeException("Bad team number");
        teams[team].setTeamNumber((byte)number);
    }
        
    
    // get/set team scores
    public synchronized short getScore(byte team) {
        return teams[team].getTeamScore();
    }

    public synchronized void setScore(byte team, short score) {
        teams[team].setTeamScore(score);
    }

    public synchronized void setScore(int team, int score) {
    	if ((score < Short.MIN_VALUE) || (score > Short.MAX_VALUE))
    		throw new RuntimeException("Bad score");
        teams[team].setTeamScore((short)score);
    }


    // get/set a penalty to a particular player
    public synchronized short getPenalty(byte team, byte player) {
        return teams[team].getPlayers()[player].getPenalty();
    }
    
    public synchronized short getPenalty(byte team, int player) {
        return teams[team].getPlayers()[player].getPenalty();
    }
    
    public synchronized short getPenalty(int team, int player) {
        return teams[team].getPlayers()[player].getPenalty();
    }
    
    public synchronized void setPenalty(byte team, byte player, short penalty) {
        teams[team].getPlayers()[player].setPenalty(penalty);
    }
    
    public synchronized void setPenalty(int team, int player, int penalty) {
    	if ((penalty < 0) || (penalty > Short.MAX_VALUE))
    		throw new RuntimeException("Bad penalty");
        teams[team].getPlayers()[player].setPenalty((short)penalty);
    }
    
    
    // set the penalty time to a particular player
    public synchronized void setSecsTillUnpenalised(byte team, byte player, short secs) {
        teams[team].getPlayers()[player].setSecsTillUnpenalised(secs);
    }

    public synchronized void setSecsTillUnpenalised(byte team, int player, int secs) {
    	if ((secs < 0) || (secs > Short.MAX_VALUE))
    		throw new RuntimeException("Bad secs till unpenalised");
        teams[team].getPlayers()[player].setSecsTillUnpenalised((short)secs);
    }
}
