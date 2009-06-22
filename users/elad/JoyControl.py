import os, sys, time
import burst
import pygame
import BasicMotion


# Constants:
threshold = 0.5
shootButton = 0
closeButton = 1

# Initialization:
pygame.init()
pygame.joystick.init()

robotStatus = ""

class JoystickWrapper(object):
    def __init__(self, x_axis=0, y_axis=1):
        self.x_axis = x_axis
        self.y_axis = y_axis
        pygame.init() # It's safe to call this method multiple times. # TODO: My memory deceived me - it doesn't specify if it is.
        pygame.joystick.init() # It's safe to call this method multiple times.
        self.joystick = pygame.joystick.Joystick(0) # Assumes one joystick in the system, I guess.
        self.joystick.init()

    @classmethod
    def update(cls):
        pygame.event.poll() # Updates the joystick to the current status.

    def get_coordinates(self):
        return (self.get_x(), self.get_y())

    def get_x(self, upToDate=False):
        if not upToDate:
            self.__class__.update()
        return self.joystick.get_axis(self.x_axis)

    def get_y(self, upToDate=False):
        if not upToDate:
            self.__class__.update()
        return -self.joystick.get_axis(self.y_axis)

    def isButtonPressed(self, buttonNumber, upToDate=False):
        if not upToDate:
            self.__class__.update()
        return self.joystick.get_button(buttonNumber) == 1

    def getStatus(self):
        return JoystickStatus(self)

    def count_buttons(self):
        return self.joystick.get_numbuttons()


class JoystickStatus(object):
    def __init__(self, joystick):
        self.joystick = joystick
        self.buttons = joystick.count_buttons() * [False]
        self.update()

    def update(self):
        pygame.event.poll()
        self.x = self.joystick.get_x(True)
        self.y = self.joystick.get_y(True)
        for i in xrange(len(self.buttons)):
            self.buttons[i] = self.joystick.isButtonPressed(i, True)


class QuitException(Exception):
    pass


class Registrat(type):
    registered = []
    def __new__(cls, name, bases, dct):
        clazz = type.__new__(cls, name, bases, dct)
        Registrat.registered.append(clazz)
        return clazz


class JoystickCommand(object):

    __metaclass__ = Registrat

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        pass

    @classmethod
    def trigger(clazz, joystickStatus):
        pass


# Exit
class ExitJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        return joystickStatus.buttons[closeButton]

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
        if "walking" in robotStatus or "turning" in robotStatus:
            BasicMotion.stopWalking()
        robotStatus = "exiting"
        raise QuitException


# Shoot
class ShootJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        global threshold
        return joystickStatus.buttons[shootButton] and abs(joystickStatus.y) < threshold and abs(joystickStatus.x) < threshold

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
        if "walking" in robotStatus or "turning" in robotStatus:
            BasicMotion.stopWalking()
        BasicMotion.shoot()
        robotStatus = "shooting"


# Stop
class StopJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        global threshold
        return abs(joystickStatus.x) < threshold and abs(joystickStatus.y) < threshold

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
        if "walking" in robotStatus or "turning" in robotStatus:
            BasicMotion.stopWalking()
        robotStatus = "at rest"


# Walk Forwards
class WalkForwardsJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        global threshold
        return joystickStatus.y > threshold and abs(joystickStatus.x) < threshold

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
        if robotStatus == "walking forwards":
            BasicMotion.addWalkStraight(0.1, 60)
        else:
            if "walking" in robotStatus or "turning" in robotStatus:
                BasicMotion.stopWalking()
            BasicMotion.slowStraightWalk(1.0)
        robotStatus = "walking forwards"


# Walk Backwards
class WalkBackwardsJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        global threshold
        return joystickStatus.y < -threshold and abs(joystickStatus.x) < threshold

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
        if robotStatus == "walking backwards":
            BasicMotion.addWalkStraight(-0.1, 60)
        else:
            if "walking" in robotStatus or "turning" in robotStatus:
                BasicMotion.stopWalking()
            BasicMotion.slowStraightWalk(-1.0)
        robotStatus = "walking backwards"


# Turn Right
class TurnRightJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        global threshold
        return abs(joystickStatus.y) < threshold and joystickStatus.x > threshold

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
        if robotStatus == "turning right":
            BasicMotion.addTurn(-1.0)
        else:
            if "walking" in robotStatus or "turning" in robotStatus:
                BasicMotion.stopWalking()
            BasicMotion.turn(-1.0)
        robotStatus = "turning right"


# Turn Left
class TurnLeftJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        global threshold
        return abs(joystickStatus.y) < threshold and joystickStatus.x < -threshold

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
        if robotStatus == "turning left":
            BasicMotion.addTurn(1.0)
        else:
            if "walking" in robotStatus or "turning" in robotStatus:
                BasicMotion.stopWalking()
            BasicMotion.turn(1.0)
        robotStatus = "turning left"


# Get Up # TODO: NOT WORKING!
def GetUpJoystickCommand(JoystickCommand):

    @classmethod
    def isTriggeredBy(clazz, joystickStatus, robotStatus):
        global threshold
        print "x"
        return abs(joystickStatus.y) < threshold and abs(joystickStatus.x) < threshold and joystickStatus.buttons[3]

    @classmethod
    def trigger(clazz, joystickStatus):
        global robotStatus
#        BasicMotion.clearPendingTasks()

        BasicMotion.getUp()
        robotStatus = "getting up"


def run():
    global robotStatus
    robotStatus = "at rest"
    joystick = JoystickWrapper(0,1)
    burst.init()

    while True:
        joystickStatus = joystick.getStatus()
        try:
            for command in Registrat.registered:
                if command.isTriggeredBy(joystickStatus, robotStatus):
                    command.trigger(joystickStatus)
                    break
        except QuitException:
            break
        time.sleep(0.001) # In either case, go to sleep for a while, so it's not THAT bad of a busy-wait.

    burst.shutdown()

if __name__ == '__main__':
    run()

