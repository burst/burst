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

import java.awt.Color;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.GraphicsDevice;
import java.awt.GraphicsEnvironment;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.event.WindowEvent;
import java.awt.image.BufferStrategy;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Properties;
import java.util.Vector;

import javax.imageio.ImageIO;
import javax.swing.JFrame;

/**
 * The main GUI of the application. 
 *
 * @author rieskamp@tzi.de
 */
public class MainGUI extends JFrame {
    private static Listen listen;
    private static java.io.PrintWriter log = null;  
    
    int w, h;
    
    private RoboCupGameControlData gameData;
    Image imageTeamRed;
    Image imageTeamBlue;
    private Date timeWhenLastPacketReceived;
    Image bgImage;
    private HashMap<String, String> teams = new HashMap<String, String>();
    private HashMap<String, Image> teamImages = new HashMap<String, Image>();
    private HashMap<String, Vector<String>> penaltyStates = new HashMap<String, Vector<String>>();
    private boolean penaltyDisplay;
    
    /**
     * 
     * @param port
     */
    public MainGUI(int port, boolean penaltyDisplay) {
        super("RoboCup GameStateVisualizer",
                GraphicsEnvironment.getLocalGraphicsEnvironment().getScreenDevices()
                [GraphicsEnvironment.getLocalGraphicsEnvironment().getScreenDevices().length - 1]
                .getDefaultConfiguration());

        System.out.println("Initializing MainGUI");
        
        this.penaltyDisplay = penaltyDisplay;
        timeWhenLastPacketReceived = new Date(0);
        gameData = new RoboCupGameControlData(Constants.TEAM_BLUE, Constants.TEAM_RED, 3);
        gameData.setHalf(true);
        gameData.setScore(Constants.TEAM_BLUE, 0);
        gameData.setScore(Constants.TEAM_RED, 0);
        gameData.setEstimatedSecs(60 * Constants.TIME_MINUTES, false);
        gameData.setTeamNumber(Constants.TEAM_BLUE, 0);
        gameData.setTeamNumber(Constants.TEAM_RED, 0);
        
        try {
            initDisplay();
        }
        catch(Exception e) {
            System.err.print(e);
        }
        
        // Load Properties
        Properties properties = new Properties();
        try {
            FileInputStream fis = new FileInputStream("teams.cfg");
            properties.load(fis);
            for(int i=1;;i++) {
            	String team = properties.getProperty(""+i, "unknown");
            	if("unknown".equals(team))
            		break;
            	teams.put(""+i, team);
            	
                String[] imageTypes = {".gif", ".jpg", ".png"};
                Image image = null;
                for(int j=0; j<imageTypes.length && image == null; j++) {
                    String source = "img" + File.separator + i + imageTypes[j];
                    File file = new File(source);
                    if(file.exists())
                        image = ImageIO.read(file);
                }
                
                if(image != null) {
                    assert image.getWidth(this) > 0 && image.getHeight(this) > 0;
                    int width  = w / 3;
                    int height = h / 3;
                    if (width * image.getHeight(this) < height * image.getWidth(this))
                        image = image.getScaledInstance(width, -1, Image.SCALE_SMOOTH);
                    else
                        image = image.getScaledInstance(-1, height, Image.SCALE_SMOOTH);
                }
                
            	teamImages.put(""+i, image);
            }
        }
        catch(IOException e) {
            logString("Error loading properties file");
        }

        listen = new Listen(port, this);
        
        // start the listening thread
        Thread listenThread = new Thread(listen);
        listenThread.start();
    }
    
    /**
     * 
     * @throws Exception
     */
    private void initDisplay() throws Exception {
        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
        setName("frmMain");
        
        // remove window frame 
        this.setUndecorated(true);
        
        // setting size to fullscreen
        GraphicsDevice[] gs = GraphicsEnvironment.getLocalGraphicsEnvironment().getScreenDevices();
        setSize(gs[gs.length - 1].getDefaultConfiguration().getBounds().getSize());
        
        // getting display resolution: width and height
        w = this.getWidth();
        h = this.getHeight();
        System.out.println("Display resolution: " + String.valueOf(w) + "x" + String.valueOf(h));
        
        // load bgimage
    	bgImage = Toolkit.getDefaultToolkit().getImage("img"+File.separator+"background.png");
    	if(bgImage != null) {
    		bgImage = bgImage.getScaledInstance(w, -1, Image.SCALE_SMOOTH);
    	}
    		
        this.setBackground(Color.WHITE);
        this.setVisible(true);
        this.createBufferStrategy(2);
    }
    
    private void close(WindowEvent evt) {
        if (Constants.debug) { System.out.println("GUI closing"); }
        listen.socketCleanup();
        if (log != null) {
            log.close();
            log = null;
        }
    }
    
    private static void logString(String s) {
        System.out.println(s);

        // open the log for appending
        try {
            if (log == null)
                log = new java.io.PrintWriter(new java.io.FileWriter(Constants.LOG_FILENAME, true));
        } 
        catch (java.io.IOException e) {
            throw new RuntimeException(e.toString());
        }
        
        log.print(new java.util.Date());
        log.print(" : ");
        log.println(s);
        log.flush();
    }
    
    private void paintBackground(Graphics g) {
    	g.drawImage(bgImage, 0, 0, this);
    }
    
    private void paintTeamImages(Graphics g) {
    	Image image = teamImages.get(""+gameData.getTeamNumber(Constants.TEAM_BLUE));
        if (image != null) {
        	if(gameData.getHalf())
        		g.drawImage(image, w / 6 - image.getWidth(this) / 2 + 5, 5 * h / 6 - image.getHeight(this) / 2 - 5, this);
        	else
        		g.drawImage(image, 5 * w / 6 - image.getWidth(this) / 2 - 5, 5 * h / 6 - image.getHeight(this) / 2 - 5, this);
        }
        image = teamImages.get(""+gameData.getTeamNumber(Constants.TEAM_RED));
        if (image != null) {
        	if(gameData.getHalf())
        		g.drawImage(image, 5 * w / 6 - image.getWidth(this) / 2 - 5, 5 * h / 6 - image.getHeight(this) / 2 - 5, this);
        	else
        		g.drawImage(image, w / 6 - image.getWidth(this) / 2 + 5, 5 * h / 6 - image.getHeight(this) / 2 - 5, this);
        }
    }
    
    private void paintGameState(Graphics g) {
        Font fontSmall = new Font (Font.DIALOG, Font.BOLD, h / 13);
        
        String teamA = teams.get(""+gameData.getTeamNumber(Constants.TEAM_BLUE));
	    if(teamA != null) {
	        g.setFont(fontSmall);
	        FontMetrics fm = g.getFontMetrics();
	           
	    	g.setColor(Color.BLUE);
	        if(gameData.getHalf()) {
	        	if(fm.stringWidth(teamA) > w / 3) // left-aligned
	        		g.drawString(teamA, 5, 3 * h / 5);
	        	else // centered
	        		g.drawString(teamA, w / 6 - (fm.stringWidth(teamA) / 2) + 5 , 3 * h / 5);
	        }
	        else {
	        	if(fm.stringWidth(teamA) > w / 3) // right-aligned
	        		g.drawString(teamA, w - 5 - fm.stringWidth(teamA), 3 * h / 5);
	        	else // centered
	        		g.drawString(teamA, 5 * w / 6 - (fm.stringWidth(teamA) / 2) - 5, 3 * h / 5);
	        }
	    }
	    
	    String teamB = teams.get(""+gameData.getTeamNumber(Constants.TEAM_RED));
	    
        if(teamB != null) {
        	g.setFont(fontSmall);
        	FontMetrics fm = g.getFontMetrics();
        	g.setColor(Color.RED);
	        if(gameData.getHalf()) {
	        	if(fm.stringWidth(teamB) > w / 3) // right-aligned
	        		g.drawString(teamB, w - 5 - fm.stringWidth(teamB), 3 * h / 5);
	        	else // centered
	        		g.drawString(teamB, 5 * w / 6 - (fm.stringWidth(teamB) / 2) - 5, 3 * h / 5);
	        }
	        else {
	        	if(fm.stringWidth(teamB) > w / 3) // left-aligned
	        		g.drawString(teamB, 5, 3 * h / 5);
	        	else // centered
	        		g.drawString(teamB, w / 6 - (fm.stringWidth(teamB) / 2) + 5 , 3 * h / 5);
	        }
        }
        
        Font fontBig = new Font (Font.DIALOG, Font.BOLD, 2 * h / 5);
        g.setFont(fontBig);
        FontMetrics fm = g.getFontMetrics();
        
        if(timeWhenLastPacketReceived.getTime() > 0) {
	        
	        // Score DEVIDER
	        g.setColor(Color.BLACK);
	        g.drawString(":", w / 2 - (fm.stringWidth(":") / 2), 1 * h / 2);
	        // Score BLUE
	        String scoreBlue = ""+gameData.getScore(Constants.TEAM_BLUE);
	        // Score RED
	        String scoreRed = ""+gameData.getScore(Constants.TEAM_RED);
	        
	        g.setColor(Color.BLUE);
	        if(gameData.getHalf())
	        	g.drawString(scoreBlue, w / 3 - (fm.stringWidth(scoreBlue) / 2), 1 * h / 2);
	        else
	        	g.drawString(scoreBlue, 2 * w / 3 - (fm.stringWidth(scoreBlue) / 2), 1 * h / 2);
	        
	        g.setColor(Color.RED);
	        if(gameData.getHalf())
	        	g.drawString(scoreRed, 2 * w / 3 - (fm.stringWidth(scoreRed) / 2), 1 * h / 2);      
	        else
	        	g.drawString(scoreRed, w / 3 - (fm.stringWidth(scoreRed) / 2), 1 * h / 2);
	        
	        Font fontPenalty = new Font(Font.DIALOG, Font.BOLD, h / 16);
	        g.setFont(fontPenalty);
	        fm = g.getFontMetrics();
	        if(gameData.getSecondaryGameState() == Constants.STATE2_PENALTYSHOOT && penaltyDisplay) {
	        	g.setColor(Color.BLUE);
	        	Vector<String> statesBlue = this.getPenaltyStates().get(""+(int)gameData.getTeamNumber(Constants.TEAM_BLUE));
	        	if(statesBlue != null) {
		        	for(int i=0; i<statesBlue.size(); i++) {
		        		String str = statesBlue.get(i);
		        		if(gameData.getHalf())
		        			g.drawString(str, 5 + i * (fm.stringWidth(str) + 5), h / 2);
		        		else
		        			g.drawString(str, w - (i+1) * (fm.stringWidth(str) + 5) - 5, h / 2);
		        	}
	        	}
	        	
	        	g.setColor(Color.RED);
	        	Vector<String> statesRed = this.getPenaltyStates().get(""+(int)gameData.getTeamNumber(Constants.TEAM_RED));
	        	if(statesRed != null) {
	        		for(int i=0; i<statesRed.size(); i++) {
		        		String str = statesRed.get(i);
		        		if(gameData.getHalf())
		        			g.drawString(str, w - (i+1) * (fm.stringWidth(str) + 5) - 5, h / 2);
		        		else
		        			g.drawString(str, 5 + i * (fm.stringWidth(str) + 5), h / 2);
		        	}
	        	}
	        }
	        
	        Font fontMiddle = new Font (Font.DIALOG, Font.BOLD, h / 8);
	        g.setFont(fontMiddle);
	        fm = g.getFontMetrics();
	        // Half
	        g.setColor(Color.BLACK);
	        String half = "";
	        if(gameData.getSecondaryGameState() == Constants.STATE2_NORMAL) {
		        if(gameData.getHalf())
		            half = "1st Half";
		        else
		            half = "2nd Half";
		        
		        g.drawString(half, w / 2 - (fm.stringWidth(half) / 2), 4 * h / 5);
	        }
	        else {
	        	half = "Penalty";
	            g.setFont(new Font (Font.DIALOG, Font.BOLD, h / 11));
	            fm = g.getFontMetrics();
	        	g.drawString(half, w / 2 - (fm.stringWidth(half) / 2),(int)( 3.7 * h / 5));
	        	g.drawString("Shoot-out", w / 2 - (fm.stringWidth("Shoot-out") / 2),(int)( 4.1 * h / 5));
	        }
	        
	        g.setFont(fontMiddle);
	        fm = g.getFontMetrics();
	        
	        // Time
	        SimpleDateFormat format = new SimpleDateFormat("mm:ss");
	        String time = format.format(new Date(gameData.getEstimatedSecs()*1000));
	        g.drawString(time, w / 2 - (fm.stringWidth(time) / 2), 19 * h / 20);
        }
    }
    
    public void update(Graphics g) {
        BufferStrategy bs = this.getBufferStrategy();
        if (bs != null)
            g = bs.getDrawGraphics();
        g.clearRect(0, 0, w, h);
        paintGameState(g);
        //paintTimeSinceLastPacketReceived();
        g.dispose();
        if (bs != null)
            bs.show();
        Toolkit.getDefaultToolkit().sync(); 
    }
    
    public void paint(Graphics g) {
        BufferStrategy bs = this.getBufferStrategy();
        if (bs != null)
            g = bs.getDrawGraphics();
        g.clearRect(0, 0, w, h);
        paintBackground(g);
        paintTeamImages(g);
        paintGameState(g);
        //paintTimeSinceLastPacketReceived();
        g.dispose();
        if (bs != null)
        	bs.show();
        Toolkit.getDefaultToolkit().sync(); 
    }
    
    public RoboCupGameControlData getGameData() {
        return gameData;
    }
    
    public void setTimeWhenLastPacketReceived(Date timeWhenLastPacketReceived) {
        this.timeWhenLastPacketReceived = timeWhenLastPacketReceived;
    }

	public HashMap<String, Vector<String>> getPenaltyStates() {
		return penaltyStates;
	}
}
