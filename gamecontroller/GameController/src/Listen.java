/*
    Copyright (C) 2006  University Of New South Wales

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
import java.net.InetAddress;
import java.nio.ByteBuffer;

public class Listen implements Runnable {      

    private boolean stopController = false;

    private MainGUI gui;

    // some objects for networking
    private DatagramSocket listen;      // socket for broadcasting
    private int port;                   // port to listen on    
	private ByteBuffer packetData;      // the packet data
	private DatagramPacket packet;      // an incomming packet
        
    private int[] teams;                // the teams we're listening for
    
    static final int packetSize = 16;   // the size of the return packet

    public static final String STRUCT_HEADER = "RGrt";
    static final int STRUCT_VERSION = 1;
    
    static class ReusingDatagramSocket extends DatagramSocket {
        public ReusingDatagramSocket(int port) throws SocketException {
            super(port);
        }
        
        public void bind(SocketAddress addr) throws SocketException {
            setReuseAddress(true);
            super.bind(addr);
        }
    }

    /** Creates a new instance of GameController */
    // it is given a reference to the data structure to broadcast, the
    // broadcast address and port
    public Listen(int[] teams, int port, MainGUI gui) {
        
        try {   
            listen = new ReusingDatagramSocket(port);
            byte[] buf = new byte[packetSize*2];
            packet = new DatagramPacket(buf, packetSize*2);
            this.port = port;
            this.gui = gui;
            this.teams = teams;
            packetData  = ByteBuffer.allocate(packetSize*3);
			packetData.order(Constants.PACKET_BYTEORDER);
        } catch (Exception err) {
            System.err.println("GameController (constructor) error: " + 
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
				if (!STRUCT_HEADER.equals(new String(header))) {
					if (Constants.debug) { System.out.println("Bad header"); }
					continue;
				}
				
				int version = packetData.getInt();
				if (version != STRUCT_VERSION) {
					if (Constants.debug) {
						System.out.println("Bad packet version: "
							+ version + " expecting: " + STRUCT_VERSION);
					}
					continue;
				}
				
				short team = packetData.getShort();
				boolean foundTeam = false;
				for (int i=0; i<teams.length && !foundTeam; i++) {
					if (team == teams[i])
						foundTeam = true;
				}
				if (!foundTeam) {
					if (Constants.debug) { System.out.println("Packet for different team: " + team); }
					continue;
				}
				
				short player = packetData.getShort();
				if ((player < 1) || (player > 11)) {
					if (Constants.debug) { System.out.println("Player out of range: " + player); }
					continue;
				}
				
				int message = packetData.getInt();
				
				switch (message) {
					case Constants.RETURN_PACKET_PENALISE:	// dog has been manually penalised
						gui.applyPenalty(team, player, Constants.PENALTY_MANUAL);
						break;
					case Constants.RETURN_PACKET_UNPENALISE:  // dog has been manually unpenalised
						gui.applyPenalty(team, player, Constants.PENALTY_NONE);
						break;
					default:
						if (Constants.debug) {
							System.out.println("Unknown message, " + message +
								", from player " + player + " on team " + team);
						}
						break;
				}
				
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
            if (Constants.debug) { System.out.println("Stopping broadcast thread"); }
            stopController = true;
            if (Constants.debug) { System.out.println("Closing broadcast socket"); }
            listen.close();   
        } catch (Exception err) {
            System.err.println("socketCleanup error: " + err.getMessage());
            System.exit(1);
        }
    }
    
}

