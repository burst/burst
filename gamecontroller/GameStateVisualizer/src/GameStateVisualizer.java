/*
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

/**
 * The starting point of the application.
 * Use command line switch "-p" to deactivate drawing the score sheet (the dots) 
 * during penalty shoutout, because it is not stateless (in contrast to everything
 * else).
 * @author rieskamp@tzi.de
 */
public class GameStateVisualizer {
    public static void main(String args[]) {
        boolean penaltyDisplay = true;
        if(args.length > 0 && "-p".equals(args[0]))
            penaltyDisplay = false;
        new MainGUI(Constants.NETWORK_DATA_PORT, penaltyDisplay);
    }
}
