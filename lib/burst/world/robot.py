from .objects import Movable
from ..consts import *
from ..eventmanager import Deferred

class Motion(object):
    
    def __init__(self, event, deferred, start_time, duration):
        self.event = event
        self.deferred = deferred
        self.has_started = False
        self.start_time = start_time
        self.duration = duration

class SerialPostQueue(object):

    """ Queue of serial events for Robot.
    
    Why this is here:
     Workaround for missing isFinished on ALMotion proxy.
    There is a isRunning, but if we call it before the motion has started, it
    will also say "False", so we need to know when the motion is supposed to
    have been already done. This is a specialization for the case of multiple
    consecutive motions, like head moves and walks. We just remember the time
    of the last finished move, and the expected duration of the move after that,
    etc.
    """

    def __init__(self, name, world):
        self._name = name
        self._posts = []
        self._world = world
        self._motion = world._motion
        self._start_time = None

    def isNotEmpty(self):
        return len(self._posts) > 0

    def add(self, postid, event, duration):
        deferred = Deferred(data=postid)
        # we keep for each move: postid -> (event code, deferred, start time, duration)
        if self._start_time is None:
            self._start_time = self._world.time
        self._posts.append([postid, event, deferred, duration])
        return deferred

    def calc_events(self, events, deferreds):
        if len(self._posts) == 0: return
        postid, event, deferred, duration = self._posts[0]
    
        #print "DEBUG: %s: waiting for %s, event %s, duration %3.2f, final_time-cur_time %3.2f, isRunning %s" % (
        #    self._name, postid, event, duration, self._start_time + duration - self._world.time, self._motion.isRunning(postid)
        #)
        if self._world.time >= self._start_time + duration and not self._motion.isRunning(postid):
            #print "DEBUG: %s: deleting %s, left %s" % (self._name, postid, len(self._posts) - 1)
            events.add(event)
            deferreds.append(deferred)
            del self._posts[0]
            if len(self._posts) == 0:
                self._start_time = None
            else:
                # DANGEROUS: We assume next head move starts immediately after the last.
                self._start_time = self._world.time

class Robot(Movable):
    _name = 'Robot'

    def __init__(self, world):
        super(Robot, self).__init__(world=world,
            real_length=ROBOT_DIAMETER)
        self._motion_posts = {}
        self._head_posts   = SerialPostQueue('head', world)
        self._walk_posts   = SerialPostQueue('walk', world)
    
    def add_expected_motion_post(self, postid, event, duration):
        deferred = Deferred(data=postid)
        self._motion_posts[postid] = Motion(event, deferred, self._world.time, duration)
        return deferred

    def add_expected_head_post(self, postid, event, duration):
        return self._head_posts.add(postid, event, duration)

    def add_expected_walk_post(self, postid, event, duration):
        print "DEBUG: adding walk %s, duration %s" % (postid, duration)
        return self._walk_posts.add(postid, event, duration)

    def isMotionInProgress(self):
        return len(self._motion_posts) > 0
    
    def isHeadMotionInProgress(self):
        return self._head_posts.isNotEmpty()
        
    def calc_events(self, events, deferreds):
        """ check if any of the motions are complete, return corresponding events
        from self._motion_posts and self._

        Check if the robot has fallen down. If it has, fire the appropriate event.
        
        we check first that the actions have started, and then that they are done.
        we use the duration - each move must be passed the duration, and not isRunning, to fire
        
        currently we treat the motion and head differently:
         motion - assume parallel, doesn't work if we check isRunning before motion started. (missing isFinished..)
         head   - only check the first event in the list 
        """
        def filter(dictionary, visitor):
            deleted_posts = [(postid, motion) for postid, motion
                        in dictionary.items() if visitor(postid, motion)]
            for postid, motion in deleted_posts:
                del dictionary[postid]
                
        def isMotionFinished(postid, motion):
            m = motion
            if m.duration > MOTION_FINISHED_MIN_DURATION:
                if not m.has_started and self._motion.isRunning(postid):
                    #print "DEBUG: motion <postid=%s> has started" % postid
                    m.has_started = True
                    m.start_time = self._world.time
                    return False
            if self._world.time >= m.start_time + m.duration and not self._motion.isRunning(postid):
                events.add(m.event)
                deferreds.append(m.deferred) # Note: order of deferred callbacks is determined here.. bugs expected
                return True
            return False
        
        filter(self._motion_posts, isMotionFinished)
        self._head_posts.calc_events(events, deferreds)
        self._walk_posts.calc_events(events, deferreds)
        

