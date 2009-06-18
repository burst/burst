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

/*
 * TeamInfo.java
 *
 * Created on 10 January 2005, 12:21
 */

/**
 * TeamInfo is part of the RoboCupGameControlData data structure. The class can 
 * convert itself into a little endian byte array for sending over a network
 *
 * @author willu@cse.unsw.edu.au shnl327@cse.unsw.edu.au
 */
public class TeamInfo {
    
    
    // each team has 4 players, ie, it requires 4 RobotInfos
    private RobotInfo[] players;
    private byte teamNumber;
    private byte teamColour;
    private short score;
    
        
    /** Creates a new instance of TeamInfo, initialise the 4 robots on the team */
    public TeamInfo() {
    }
    
    // constructor that sets the team colour and number
    public TeamInfo(byte teamColour, byte teamNumber, int numPlayers) {        
        this.teamColour = teamColour;
        this.teamNumber = teamNumber;
        players = new RobotInfo[Constants.MAX_NUM_PLAYERS];
        for (int i=0; i<Constants.MAX_NUM_PLAYERS; i++) {
        	players[i] = new RobotInfo();
        }
    }    
    
    // convert the team into a string
    public String toString() {        
        StringBuffer teamString = new StringBuffer();
        
        teamString.append("Team#:" + teamNumber + " " +
                            "TeamCol:" + teamColour + " " + 
                            "Score:" + score + " ");
        
        for (int i=0; i<players.length; i++) {
        	teamString.append("p" + i + ":");
        	teamString.append(players[i].toString());
        	teamString.append(' ');
        }
        
        return teamString.toString();
    }
           
    
    // get the robots in the team, return as an array
    public RobotInfo[] getPlayers() {
        return players;
    }
    
    
    // get/set the team number
    public void setTeamNumber(byte teamNumber) {
        this.teamNumber = teamNumber;
    }
    
    public byte getTeamNumber() {
        return this.teamNumber;
    }    
     
    
    // get/set team colour
    public void setTeamColour(byte teamColour) {
        this.teamColour = teamColour;
    }
    
    public byte getTeamColour() {
        return this.teamColour;
    }   
    
        
    // get/set team score
    public void setTeamScore(short score) {
        this.score = score;
    }
    
    public void setTeamScore(int score) {
    	if ((score < Short.MIN_VALUE) || (score > Short.MAX_VALUE))
    		throw new RuntimeException("Bad score");
        this.score = (short)score;
    }
    
    public short getTeamScore() {
        return this.score;
    }    
}
