#!/usr/bin/env python
import termios, fcntl, sys, os

# The routines ready_stdin, read_key, and restore_stdin are a reformulation
# of the following Stack Overflow answer:
#     http://stackoverflow.com/a/6599441 

def ready_stdin():
  fd = sys.stdin.fileno()
  flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
  attrs_save = termios.tcgetattr(fd)
  attrs = list(attrs_save)
  attrs[0] &= ~(termios.IGNBRK | \
                termios.BRKINT | \
                termios.PARMRK | \
                termios.ISTRIP | \
                termios.INLCR  | \
                termios.IGNCR  | \
                termios.ICRNL  | \
                termios.IXON)
  attrs[1] &= ~termios.OPOST
  attrs[2] &= ~(termios.CSIZE | \
                termios.PARENB)
  attrs[2] |= termios.CS8
  attrs[3] &= ~(termios.ECHONL | \
                termios.ECHO   | \
                termios.ICANON | \
                termios.ISIG   | \
                termios.IEXTEN)
  fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
  return fd, attrs, attrs_save, flags_save

def read_key(fd,attrs,attrs_save,flags_save):
  # TODO: Figure out how to avoid setting and resetting tc on each read
  termios.tcsetattr(fd, termios.TCSANOW, attrs)
  try:
    ret = sys.stdin.read(1)
  except KeyboardInterrupt:
    ret = 0
  termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
  return ret

def restore_stdin(fd,attrs,attrs_save,flags_save):
  termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
  fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)

def start(print_progress = True):
  """
  This is for recording a small number of events for two mice in a cage via
  the following keypresses:
  
  'a': Allogrooming (grooming the unconscious mouse)
  
  'b': Burrowing (rummaging under bedding or other mouse)
  
  'c': Climbing cage
  
  'g': Grooming self
  
  'n': Nesting behavior (bringing materials or building nest)
  
  'r': Rearing (forepaws in air)
  
  's': Sitting
  
  'o': Other (blank state).

  Additionally, 'q' quits and 'p' pauses/unpauses the recording process.
  """
  import time
  from collections import defaultdict
  time_delta = time.time()
  paused = False
  
  actions = defaultdict(list)
  labels = defaultdict()
  labels['a'] = 'Allogrooming'
  labels['b'] = 'Burrowing'
  labels['c'] = 'Climbing'
  labels['g'] = 'Grooming'
  labels['n'] = 'Nesting'
  labels['o'] = 'Other'
  labels['r'] = 'Rearing'
  labels['s'] = 'Sitting'

  # Initialize in the 'other' state
  action_start = 0
  action_type = 'o'

  # Ready stdin for reading a single key
  stdin_state = ready_stdin()

  while True:
    key = read_key(*stdin_state)
    curr_time = time.time() - time_delta

    if key == 'q':
      actions[action_type].append((action_start, curr_time))
      totals = ()
      used_labels = ()
      for char, segments in actions.items():
        total = 0
        for beg, end in segments:
          total = total + (end - beg)
        totals = totals + (total,)
        used_labels = used_labels + (labels[char],)
        print ''
        print '%s (%f seconds)' % (labels[char], total)
        print segments

      try:
        import matplotlib.pyplot as plt
        plt.pie(totals, labels=used_labels, \
        autopct='%1.1f%%', shadow=True)
        plt.axis('equal')
        plt.show()
      except:
        print 'WARNING: Could not import pyplot'

      break

    elif key == ' ':
      if paused:
        pause_time = curr_time - pause_start
        time_delta = time_delta + pause_time
        paused = False
        print "Ended %f second pause" % pause_time
      else:
        pause_start = curr_time
        paused = True
        print "Pausing"

    elif not paused:
      if key != 'a' and \
         key != 'b' and \
         key != 'c' and \
         key != 'g' and \
         key != 'n' and \
         key != 'o' and \
         key != 'r' and \
         key != 's':
        print "WARNING: Unrecognized key of %s; changing to 'o'" % key
        key = 'o'

      if print_progress:
        print 'Marking as %s at %f seconds' % (labels[key], curr_time)

      if action_type != key:
        actions[action_type].append((action_start, curr_time))
        action_type = key
        action_start = curr_time

  # Put stdin back to normal before exiting
  restore_stdin(*stdin_state)

  return actions

if __name__ == "__main__":
  start()
