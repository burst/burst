import burst
from burst_util import (BurstDeferred, DeferredList, succeed)
from burst_consts import MOTION_FINISHED_MIN_DURATION

################################################################################

class Motion(object):
    
    def __init__(self, event, deferred, start_time, duration):
        self.event = event
        self.deferred = deferred
        self.has_started = False
        self.start_time = start_time
        self.duration = duration

################################################################################

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
        # print stuff
        self.verbose = burst.options.verbose_movecoordinator

    def isNotEmpty(self):
        return len(self._posts) > 0

    def add(self, postid, event, duration):
        deferred = BurstDeferred(data=postid)
        # we keep for each move: postid -> (event code, deferred, start time, duration)
        if self._start_time is None:
            self._start_time = self._world.time
        self._posts.append([postid, event, deferred, duration])
        return deferred

    def calc_events(self, events, deferreds):
        if len(self._posts) == 0: return

        self._events, self._deferreds = events, deferreds # this will become usual for all these objects

        postid, event, deferred, duration = self._posts[0]
        if event is None and deferred is None:
            print "ERROR: SerialPostQueue: handling an empty post?"
            import pdb; pdb.set_trace()
    
        #print "DEBUG: %s: waiting for %s, event %s, duration %3.2f, final_time-cur_time %3.2f, isRunning %s" % (
        #    self._name, postid, event, duration, self._start_time + duration - self._world.time, self._motion.isRunning(postid)
        #)
        if self._world.time >= self._start_time + duration:
            if not isinstance(postid, int):
                import pdb; pdb.set_trace()
            self._motion.isRunning(postid).addCallback(
                lambda result, postid=postid, event=event, deferred=deferred:
                    self._onIsRunning(result, postid, event, deferred))

    def _onIsRunning(self, result, postid, event, deferred):
        # We could be called a second time with the same postid after actually having finished.
        # this can happend when using the twisted event loop, since we issue the isRunning
        # code async to the callbacks, possibly several callbacks will be fired at once.
        # so the upshot is being careful about checking if we are still relevant.
        # TODO: the real fix is not calling isRunning while an outgoing call is in progress.
        if result: return
        if len(self._posts) == 0:
            if self.verbose:
                print "FIXME: SerialPostQueue._onIsRunning called twice for postid = %s" % postid
            return
        if self._posts[0][0] != postid:
            import pdb; pdb.set_trace()
        self._events.add(event)
        self._deferreds.append(deferred)
        if self.verbose:
            print "SerialPostQueue: (%s) Deleting %s" % ([x[0] for x in self._posts], postid)
        del self._posts[0]
        if len(self._posts) == 0:
            self._start_time = None
        else:
            # DANGEROUS: We assume next head move starts immediately
            # after the last.
            self._start_time = self._world.time

################################################################################

class MoveCoordinator(object):

    """ All low level moves, where low level is defined by anything
    we talk to naoqi to do, so this includes:
    forward walk, sidestep walk, arc walk, turn
    joint moves (doMove)
    
    They are recorded here, checked for completion here, and we call
    user callbacks from here.

    This replaces old code in actions.__init__ and world.robot
     - it reuses all of the queue stuff, but it is moved from world.robot
     here. This allows for easy debugging - I just got back this postid,
     what action was it for? who created it?
    """

    debug = burst.options.debug

    def __init__(self, world):
        self._world = world
        # HACK - Add ourselves to the list of updated objects,
        # so calc_events is called. Basically until now all such objects
        # were constructed in world, but world doesn't depend on actions.
        self._motion = self._world._motion
        self._motion_posts = {}
        self._head_posts   = SerialPostQueue('head', self._world)
        self._walk_posts   = SerialPostQueue('walk', self._world)
        self._initiated = []
        self._posted = []
        # helpers
        self._post_handler = {'motion': self._add_expected_motion_post,
            'head':self._add_expected_head_post,
            'walk':self._add_expected_walk_post}
        # debug
        if self.debug:
            self._delete_times = []

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

        # TODO: Use profiling to see if the redefinition of this filter every frame is something that's worth avoiding.

        def filter(dictionary, visitor):
            def collectResults(results):
                deleted_posts = [result for success, result in results]
                for postid in deleted_posts:
                    if postid:
                        #print "DOUBLE YAY deleting motion postid=%s" % postid
                        if postid in dictionary:
                            del dictionary[postid]
                            if self.debug:
                                self._delete_times.append((self._world.time, postid))
                        else:
                            print "DEBUG ME: postid to be deleted but not in dictionary"
                            import pdb; pdb.set_trace()
            DeferredList([visitor(postid, motion).addCallback(
                lambda result, postid=postid: result and postid)
                    for postid, motion in dictionary.items()]).addCallback(collectResults)
                
        def isMotionFinished(postid, motion):
            m = motion
            if ((m.duration > MOTION_FINISHED_MIN_DURATION and not m.has_started)
                or (self._world.time >= m.start_time + m.duration)):
                    if not isinstance(postid, int):
                        import pdb; pdb.set_trace()
                    return self._motion.isRunning(postid).addCallback(
                        lambda result, m=m, postid=postid: onIsRunning(result, m, postid))
            return succeed(False)
        
        def onIsRunning(isrunning, m, postid):
            #print "DEBUG: motion <postid=%s> has started" % postid
            if m.duration > MOTION_FINISHED_MIN_DURATION and not m.has_started and isrunning:
                m.has_started = True
                m.start_time = self._world.time
                return False
            if self._world.time >= m.start_time + m.duration and not isrunning:
                #print "DEBUG: Robot Head Motions: %s done!" % postid
                self._events.add(m.event)
                self._deferreds.append(m.deferred) # Note: order of deferred callbacks is determined here.. bugs expected
                return True
            return False

        self._events, self._deferreds = events, deferreds

        filter(self._motion_posts, isMotionFinished)
        self._head_posts.calc_events(events, deferreds)
        self._walk_posts.calc_events(events, deferreds)

    def _add_expected_motion_post(self, postid, event, duration):
        deferred = BurstDeferred(data=postid)
        self._motion_posts[postid] = Motion(event, deferred, self._world.time, duration)
        return deferred

    def _add_expected_head_post(self, postid, event, duration):
        return self._head_posts.add(postid, event, duration)

    def _add_expected_walk_post(self, postid, event, duration):
        print "DEBUG: adding walk %s, duration %s" % (postid, duration)
        return self._walk_posts.add(postid, event, duration)

    def add_expected_walk_post(self, description, postid, event, duration):
        """ HACK for Journey - Journey currently does the deferreds itself,
        not using the BurstDeferred wrappers we provide, so to still log
        anything it does we provide the old interface, with added description.
        We use the initiate time as now (so it is actually the postid time,
        almost the same)
        """
        initiated = self._add_initiated(time=self._world.time, kind='walk',
            description=description, event=event, duration=duration)
        self._add_posted(postid, initiated)
        return self._add_expected_walk_post(postid=postid, event=event, duration=duration)

    def _add_initiated(self, time, kind, description, event, duration):
        initiated = len(self._initiated)
        motion = (self._world.time, kind, description, event, duration)
        self._initiated.append(motion)
        if kind is 'walk':
            self._world.odometry.onWalkInitiated(self._world.time, description, duration)
        return initiated

    def isMotionInProgress(self):
        return len(self._motion_posts) > 0
    
    def isHeadMotionInProgress(self):
        return self._head_posts.isNotEmpty()
  
    def waitOnPostid(self, d, description, kind, event, duration):
        """ Wait on a postid given a Deferred. Records
        the description of the intiated action, and returns a BurstDeferred.

        description - this is kinda a 'command' but we use it just for logging. So a little
            redundancy in calling, instead of adding "magic" to extract it.
        d - deferred for the post, will return a postid
        event - event to be fired
        duration - expected duration of action
        """
        #TODO: a MoveCommand object.. end up copying northernbites after all, just in the hard way.
        initiated = self._add_initiated(self._world.time, kind, description, event, duration)
        bd = BurstDeferred(None)
        d.addCallback(lambda postid, initiated=initiated, bd=bd:
            self._onPostId(postid, initiated, bd))
        return bd

    def _add_posted(self, postid, initiated):
        self._posted.append((postid, self._initiated[initiated]))

    def _onPostId(self, postid, initiated, bd):
        if not isinstance(postid, int):
            print "ERROR: onPostId with Bad PostId: %s" % repr(postid)
            print "ERROR:  Did you forget to enable ALMotion perhaps?"
            raise SystemExit
        initiate_time, kind, description, event, duration = self._initiated[initiated]
        self._add_posted(postid, initiated)
        self._post_handler[kind](postid, event, duration).onDone(bd.callOnDone)

