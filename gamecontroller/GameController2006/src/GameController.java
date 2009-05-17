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
 * GameController.java
 *
 * Created on 14 January 2005, 10:34
 */

/**
 * This is the starting class. Its really just a wrapper to start MainGUI. From
 * there the GUI, data structure, and network code are initialised.
 *
 * @author willu@cse.unsw.edu.au shnl327@cse.unsw.edu.au
 */
public class GameController {
    
    
    public static void main(String args[]) {
        
        int blueNumber = 0;     // team numbers
        int redNumber  = 0;
        
        // command line argument defaults, uses these of the arguments don't
        // modify them
        String broadcast = Constants.NETWORK_BROADCAST;     // broadcast address
        int    port      = Constants.NETWORK_DATA_PORT;     // default port
        Constants.debug  = false;
        boolean quiet    = false;
        int numplayers   = 4;
        
        
        // check there are at least the blue and red team numbers
        if (args.length < 2) {
            System.err.println(Constants.HELP);            
            System.exit(1);
        }
                
        // the last two arguments will always be the team numbers
        blueNumber = Integer.parseInt(args[args.length-2]);
        redNumber  = Integer.parseInt(args[args.length-1]);
        
        
        // scan each argument looking for specific switches
        for (int i=0; i<args.length; i++) {
            
            // look for turned on debug switch
            if (args[i].equals(Constants.ARG_DEBUG)) {
                Constants.debug = true;
                System.out.println("Debugging on");
            }
            
            // look for turned on quiet switch
            if (args[i].equals(Constants.ARG_QUIET)) {
                quiet = true;
                System.out.println("Sound suppressed");
            }
            
            // look for the port switch
            if (args[i].equals(Constants.ARG_PORT)) {
                port = Integer.parseInt(args[i+1]);
            }
            
            // look for the broadcast switch
            if (args[i].equals(Constants.ARG_BROADCAST)) {
                broadcast = args[i+1];
            }
            
            // look for the number of players switch
            if (args[i].equals(Constants.ARG_NUMPLAYERS)) {
                numplayers = Integer.parseInt(args[i+1]);
            }
            
        }
        
        // check for the debug command line option
        if (!Constants.debug) { System.out.println("Debugging off");  }
                        
        if (Constants.debug) { 
            System.out.println("Blue is " + blueNumber + ", Red is " + redNumber); 
            System.out.println("Using broadcast address: " + broadcast);
            System.out.println("Using port " + port + " for broadcast");
            System.out.println("Handling " + numplayers + " players per team");
        }
        
        
        // star the GUI
        new MainGUI(blueNumber, redNumber, broadcast, port, numplayers, quiet).setVisible(true);
                
    }
    
}
