/*
    Copyright (C) 2006  University Of New South Wales
    Copyright (C) 2009  University of Bremen

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

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketAddress;
import java.net.SocketException;
import java.nio.ByteBuffer;
import java.util.Date;
import java.util.Vector;

/**
 * The class listens to the packages sent by the GameContoller. 
 *
 * @author rieskamp@tzi.de
 */
public class Listen implements Runnable {      

    private boolean stopController = false;

    private MainGUI gui;

    // some objects for networking
    private DatagramSocket listen;      // socket for broadcasting
	private ByteBuffer packetData;      // the packet data
	private DatagramPacket packet;      // an incomming packet
    
	private boolean penaltySuccess = false;
	
    static final int packetSize = RoboCupGameControlData.packet_size;   // the size of the return packet
    
    static class ReusingDatagramSocket extends DatagramSocket {
        public ReusingDatagramSocket(int port) throws SocketException {
            super(port);
        }
        
        public void bind(SocketAddress addr) throws SocketException {
            setReuseAddress(true);
            super.bind(addr);
        }
    }

    public Listen(int port, MainGUI gui) {
        
        try {
            listen = new ReusingDatagramSocket(port);

            byte[] buf = new byte[packetSize*2];
            packet = new DatagramPacket(buf, packetSize*2);
            this.gui = gui;
            packetData  = ByteBuffer.allocate(packetSize*3);
			packetData.order(Constants.PACKET_BYTEORDER);
        } catch (Exception err) {
            System.err.println("GameStateVisualizer (constructor) error: " + 
                               err.getMessage() + " " +
                               "(No network devices set up?)");
            System.exit(1);
        }
    }
    
    // broadcast loop runs in a separate thread, this is stopped by socketCleanup
    public void run() {
        while (!stopController) {
            try {
				listen.receive(packet);
				if (Constants.debug) { System.out.println("Incomming packet"); }
				if (packet.getLength() != packetSize) {
					if (Constants.debug) { System.out.println("Bad size"); }
					continue;
				}
				packetData.rewind();
				packetData.put(packet.getData());
				
				packetData.rewind();
				
				byte[] header = new byte[4];
				packetData.get(header);
				if (!RoboCupGameControlData.STRUCT_HEADER.equals(new String(header))) {
					if (Constants.debug) { System.out.println("Bad header"); }
					continue;
				}
				
				int version = packetData.getInt();
				if (version != RoboCupGameControlData.STRUCT_VERSION) {
					if (Constants.debug) {
						System.out.println("Bad packet version: "
							+ version + " expecting: " + RoboCupGameControlData.STRUCT_VERSION);
					}
					continue;
				}
				
				RoboCupGameControlData gameData = gui.getGameData();
				packetData.get(); // playersPerTeam
				byte gameState = packetData.get(); // gameState
				byte firstHalf = packetData.get(); // firstHalf
				packetData.get(); // kickOffTeam
				byte secondaryState = packetData.get(); // secondaryState
				packetData.get(); // dropInTeam
				packetData.getShort(); // dropInTime
				int secsRemaining = packetData.getInt(); // secsRemaining
				
				// team blue
				byte team1Number = packetData.get(); // teamNumber
				packetData.get(); // teamColor
				int team1Score = packetData.getShort(); // score
				packetData.position(packetData.position() + Constants.MAX_NUM_PLAYERS * 4);
				// team red
				byte team2Number = packetData.get(); // teamNumber
				packetData.get(); // teamColor
				short team2Score = packetData.getShort(); // score
				
				gameData.setGameState(gameState);
				if(gameData.getSecondaryGameState() == Constants.STATE2_NORMAL 
					&& secondaryState == Constants.STATE2_PENALTYSHOOT) {
					
					gui.getPenaltyStates().put(""+(int) team1Number, new Vector<String>());
					gui.getPenaltyStates().put(""+(int) team2Number, new Vector<String>());
					penaltySuccess = false;
				}
				if(gameData.getSecondaryGameState() == Constants.STATE2_PENALTYSHOOT
					&& gameData.getHalf() != (firstHalf == Constants.TRUE)) {
					
					if(!penaltySuccess) {
						Vector<String> statesRed = gui.getPenaltyStates().get(""+(int)gameData.getTeam(Constants.TEAM_RED).getTeamNumber());
						statesRed.add(""+'\u25CB');
						//System.out.println("Verschossen!");
					}
					else
						penaltySuccess = false;
				}
				if(gameData.getSecondaryGameState() == Constants.STATE2_PENALTYSHOOT
					&& gameData.getHalf() == (firstHalf == Constants.TRUE)
					&& gameData.getTeam(Constants.TEAM_RED).getTeamScore() < team2Score) {
					
					Vector<String> statesBlue = gui.getPenaltyStates().get(""+(int)gameData.getTeam(Constants.TEAM_RED).getTeamNumber());
					statesBlue.add(""+'\u25CF');
					//System.out.println("Getroffen!");
					penaltySuccess = true;
				}
				gameData.setSecondaryGameState(secondaryState);
				gameData.setHalf(firstHalf);
				gameData.setEstimatedSecs(secsRemaining, false);
				gameData.getTeam(Constants.TEAM_BLUE).setTeamNumber(team1Number);
				gameData.getTeam(Constants.TEAM_BLUE).setTeamScore(team1Score);
				gameData.getTeam(Constants.TEAM_RED).setTeamNumber(team2Number);
				gameData.getTeam(Constants.TEAM_RED).setTeamScore(team2Score);
				gui.setTimeWhenLastPacketReceived(new Date());
				gui.repaint();				
           } catch (IOException e) {
           		if (!stopController) {
           			System.err.println("IOException while listening for packets: " + e);
           		}
           }
        }
    }

    // called by MainGUI when program is closing
    public void socketCleanup() {
        try {
            if (Constants.debug) { System.out.println("Stopping listen thread"); }
            stopController = true;
            if (Constants.debug) { System.out.println("Closing listen socket"); }
            listen.close();   
        } catch (Exception err) {
            System.err.println("socketCleanup error: " + err.getMessage());
            System.exit(1);
        }
    }
    
}

