from threading import Thread
from Queue import Queue

from twisted.python import log

from burst_util import (DeferredList, succeed, func_name)

import burst
import movecoordinator
import burst_target

from burst_events import (EVENT_HEAD_MOVE_DONE, EVENT_BODY_MOVE_DONE,
    EVENT_CHANGE_LOCATION_DONE)
from movecoordinator import KIND_WALK

class ALProxyThread(Thread):
    """ New input from aldebaran suggests that ALProxy is blocking,
    but using multiple ALProxys, one per thread, should work. So
    the former ActionThread becomes ALProxyThread, and it won't be
    joined until the very end of the program (which is better anyhow),
    and it will now have an incoming queue to be fed new moves.
    """

    QUIT = False

    def __init__(self, *args, **kw):
        super(ALProxyThread, self).__init__(*args, **kw)
        # XXX First place where Deferred code isn't used - this will blocks..
        self._motion = burst.ALProxy('ALMotion', burst_target.ip, burst_target.port)
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.verbose = burst.options.verbose_movecoordinator

    def start(self, _=None):
        """ convenience for using with Deferred.addCallback """
        return super(ALProxyThread, self).start()

    def run(self):
        while True:
            method_getter, args, bd, description = self.in_queue.get()
            if method_getter == self.QUIT:
                # TODO: need to close the ALProxy somehow
                return
            meth = method_getter(self._motion)
            if self.verbose:
                print "%s: starting  %s" % (self.getName(), description)
            try:
                apply(meth, args)
            except Exception, e:
                print "ActionThread: EXCEPTION: %s" % e
                self.out_queue.put((False, bd, e))
            if self.verbose:
                print "%s: done      %s" % (self.getName(), description)
            self.out_queue.put((True, bd, None))

    def put(self, method_getter, args, bd, description):
        self.in_queue.put((method_getter, args, bd, description))

    def quit(self):
        self.in_queue.put((self.QUIT, None, None, None))

class ThreadedMoveCoordinator(movecoordinator.BaseMoveCoordinator):
    """ A different strategy for handling moves:
     we have a thread open on any request, it will signal
     to us when it is done via a queue.
     We have a choice of allowing queuing of commands or not - we choose
     to avoid it for now, higher level code can just hold on to those commands
     and execute them on the callback, and it already does it (SearchPlanner,
     Journey)
    """

    def __init__(self, world):
        super(ThreadedMoveCoordinator, self).__init__(world)

        class ThreadHolder(object):
            def __init__(self, *args, **kw):
                self.thread = ALProxyThread(*args, **kw)
                self.thread.start()
                self.cleaner = None
                self.busy = False # When True don't give any more motions
            def makeBusy(self, cleaner):
                self.cleaner = cleaner
                self.busy = True
                return self

        # These are not None if there is a motion of that sort, and then
        # a tuple (thread, burst_deferred)
        self._head_move_holder  = ThreadHolder(name='Head')
        self._walk_holder       = ThreadHolder(name='Walk')
        self._body_move_holder  = ThreadHolder(name='Body')

        self.verbose_threading = self.verbose and False # TODO - option

        if self.verbose_threading:
            class Watcher(Thread):
                def run(self):
                    import sys, time, threading
                    start = time.time()
                    while True:
                        sys.stdout.write('Threads: %4.2f %s\n' % (time.time() - start, threading.enumerate()))
                        sys.stdout.flush()
                        time.sleep(1)
            Watcher().start()

        if burst.options.use_postid:
            self._startAction = self._startActionPostId
        else:
            self._startAction = self._startActionStraight

    def _ensure_empty_thread(self, holder, what):
        if holder.busy:
            print "ERROR: ThreadedMoveCoordinator: You tried a second %s while first is still in progress" % what # RuntimeError
            if what == 'HEAD MOVE':
                print "     : Allowing head move (queued after current move)"
            elif what == 'WALK':
                print "     : clearing footsteps"
                self._actions.clearFootsteps()
            else:
                print "     : Allowing body move (queued after current move)"

    def _ensure_no_head_move(self):
        self._ensure_empty_thread(self._head_move_holder, 'HEAD MOVE')

    def _ensure_no_body_move(self):
        self._ensure_empty_thread(self._body_move_holder, 'BODY MOVE')

    def _ensure_no_walk_move(self):
        self._ensure_empty_thread(self._walk_holder, 'WALK')

    def _completeHeadMove(self):
        self._head_move_holder.busy = False

    def _completeWholeBodyMove(self):
        self._head_move_holder.busy = False
        self._body_move_holder.busy = False

    def _completeBodyMove(self):
        self._body_move_holder.busy = False

    def _completeWalk(self):
        self._walk_holder.busy = False

    def calc_events(self, events, deferreds):
        for holder, event in ((self._head_move_holder, EVENT_HEAD_MOVE_DONE),
                (self._body_move_holder, EVENT_BODY_MOVE_DONE),
                (self._walk_holder, EVENT_CHANGE_LOCATION_DONE)):
            thread, cleaner = holder.thread, holder.cleaner
            while not thread.out_queue.empty(): # TODO - limit this? (throttle results for easy debug? for cpu?)
                # we have something.
                success, bd, exception = thread.out_queue.get()
                if not success:
                    print "ThreadedMoveCoordinator: Caught Exception (bd=%s): %s" % (bd, exception)
                if self.verbose:
                    print "ThreadedMoveCoordinator: motion complete. %s%s, %s, %s" % (
                        thread.getName(), bd, cleaner.im_func.func_name)
                    thread.join() # is this required?
                deferreds.append(bd)
                events.add(event)
                cleaner()

    def _startAction(self, method_attr, args, holder, bd):
        print "Nothing"
        return

    def _startActionPostId(self, method_attr, args, holder, bd):
        apply(getattr(self._motion.post, method_attr), args).addCallback(
            lambda postid: holder.thread.put(
                method_getter=lambda motion: motion.wait,
                args=(postid, 0), bd=bd, description='postid %s' % method_attr)).addErrback(log.err)

    def _startActionStraight(self, method_attr, args, holder, bd):
        holder.thread.put(
            method_getter=lambda motion: getattr(motion, method_attr),
            args=args, bd=bd, description='straight %s' % method_attr)

    # User API

    def isMotionInProgress(self):
        return self._body_move_holder.busy

    def isHeadMotionInProgress(self):
        return self._head_move_holder.busy

    def doMove(self, joints, angles_matrix, durations_matrix, interp_type, description='doMove'):
        len_2 = len(joints) == 2
        has_head = 'HeadYaw' in joints or 'HeadPitch' in joints
        if len_2 and has_head:
            if self.verbose:
                print "ThreadedMoveCoordinator: doing head move"
            # Moves head only - just check that no head moves in progress
            self._ensure_no_head_move()
            holder = self._head_move_holder.makeBusy(self._completeHeadMove)
        elif has_head:
            # Moves whole body, so check no move at all nor walk is in progress
            if self.verbose:
                print "ThreadedMoveCoordinator: doing complete body move"
            self._ensure_no_head_move()
            self._ensure_no_body_move()
            self._ensure_no_walk_move()
            self._head_move_holder.busy = True
            holder = self._body_move_holder.makeBusy(self._completeWholeBodyMove)
        else:
            if self.verbose:
                print "ThreadedMoveCoordinator: doing body move"
            # a body move - check that walk and body are not in progress
            self._ensure_no_body_move()
            self._ensure_no_walk_move()
            holder = self._body_move_holder.makeBusy(self._completeBodyMove)
        bd = self._make_bd(self)
        self._startAction(method_attr='doMove',
            args=(joints, angles_matrix, durations_matrix, interp_type),
            holder=holder, bd=bd)
        return bd

    def changeChainAngles(self, chain, angles):
        # TODO - tester for this..
        if chain is "Head":
            if self.verbose:
                print "ThreadedMoveCoordinator: changeChainAngles: head"
            # Head move
            self._ensure_no_head_move()
            holder = self._head_move_holder.makeBusy(self._completeHeadMove)
        else:
            if self.verbose:
                print "ThreadedMoveCoordinator: changeChainAngles: %s" % chain
            self._ensure_no_body_move()
            holder = self._body_move_holder.makeBusy(self._completeBodyMove)
        bd = self._make_bd(self)
        self._startAction(method_attr='changeChainAngles', args=(chain, angles),
            holder=holder, bd=bd)
        return bd

    def walk(self, d, duration, description):
        if self.verbose:
            print "ThreadedMoveCoordinator: walk"
        holder = self._walk_holder.makeBusy(self._completeWalk)
        bd = self._make_bd(self)
        d.addCallback(lambda _: self._startAction(method_attr='walk', args=tuple(), holder=holder, bd=bd)).addErrback(log.err)
        self._add_initiated(time=self._world.time, kind=KIND_WALK, description=description,
            event=EVENT_CHANGE_LOCATION_DONE, # TODO: This isn't actually used - why is it here?
            duration=duration, completion_bd=bd)
        return bd

    def shutdown(self):
        print "ThreadedMoveCoordinator: closing all threads"
        for holder in (self._head_move_holder, self._body_move_holder, self._walk_holder):
            holder.thread.quit()

