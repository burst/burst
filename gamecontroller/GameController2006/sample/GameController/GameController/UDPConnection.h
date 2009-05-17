/*

   Copyright 2004 The University of New South Wales (UNSW) and National  
   ICT Australia (NICTA).

   This file is part of the 2004 team rUNSWift RoboCup entry.  You may  
   redistribute it and/or modify it under the terms of the GNU General  
   Public License as published by the Free Software Foundation; either  
   version 2 of the License, or (at your option) any later version as  
   modified below.  As the original licensors, we add the following  
   conditions to that license:

   In paragraph 2.b), the phrase "distribute or publish" should be  
   interpreted to include entry into a competition, and hence the source  
   of any derived work entered into a competition must be made available  
   to all parties involved in that competition under the terms of this  
   license.

   In addition, if the authors of a derived work publish any conference  
   proceedings, journal articles or other academic papers describing that  
   derived work, then appropriate academic citations to the original work  
   must be included in that publication.

   This rUNSWift source is distributed in the hope that it will be useful,  
   but WITHOUT ANY WARRANTY; without even the implied warranty of  
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU  
   General Public License for more details.

   You should have received a copy of the GNU General Public License along  
   with this source code; if not, write to the Free Software Foundation,  
   Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

 */

/*
 * Last modification background information
 * $Id: UDPConnection.h 4364 2004-09-22 07:04:12Z kcph007 $
 *
 * Copyright (c) 2004 UNSW
 * All Rights Reserved.
 *
**/



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

#ifndef UDPConnection_h_DEFINED
#define UDPConnection_h_DEFINED

#include <ant.h>
#include <IPAddress.h>

#ifndef _ConnectionState_enum
#define _ConnectionState_enum

enum ConnectionState {
    CONNECTION_CLOSED,
    CONNECTION_CONNECTING,
    CONNECTION_CONNECTED,
    CONNECTION_SENDING,
    CONNECTION_RECEIVING,
    CONNECTION_CLOSING
};

#endif // _ConnectionState_enum

struct UDPConnection {
    antModuleRef     endpoint;
    ConnectionState  state;

    // send buffer
    antSharedBuffer  sendBuffer;
    byte*            sendData;
    int              sendSize;
    IPAddress        sendAddress;
    Port             sendPort;
    // receive buffer
    antSharedBuffer  recvBuffer;
    byte*            recvData;
    int              recvSize;
};

#endif // UDPConnection_h_DEFINED
