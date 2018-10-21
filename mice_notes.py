#!/usr/bin/env python

#
#  Copyright 2016, Jack Poulson
#  All rights reserved.
#
#  This file is part of mice_notes and is under the BSD 2-Clause License,
#  which can be found in the LICENSE file in the root directory, or at
#  http://opensource.org/licenses/BSD-2-Clause
#

import termios, fcntl, sys, os

# The routines ready_stdin, read_key, and restore_stdin are a reformulation
# of the following Stack Overflow answer:
#     http://stackoverflow.com/a/6599441 

def ready_stdin():
  "This is a docstring for ready_stdin..."
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
  
  'd': Digging near mouse
  
  'g': Grooming self

  'f': Fluffing own nest
  
  'n': Nesting behavior (bringing materials or dragging mouse)
  
  'r': Rearing (forepaws in air or against wall)
  
  's': Sitting
  
  'o': Other (blank state).

  'm': Pulling hair or aggressive behavior

  'w': Paw Withdrawal or licking

  Additionally, 'q' quits and 'p' pauses/unpauses the recording process.
  """
  import time
  from collections import defaultdict
  time_delta = time.time()
  paused = False

  labels = defaultdict()
  labels['a'] = 'Allogrooming'
  labels['b'] = 'Burrowing'
  labels['d'] = 'Digging near mouse'  
  labels['g'] = 'Grooming'
  labels['f'] = 'Fluffing own nest'
  labels['n'] = 'Nesting'
  labels['o'] = 'Other'
  labels['r'] = 'Rearing/Climbing'
  labels['s'] = 'Side-by-Side'
  labels['m'] = 'Pulling/Aggressive'
  labels['w'] = 'Withdrawal/Attention'

  colors = defaultdict()
  colors['a'] = "#0000E6"
  colors['b'] = "#FF6666"
  colors['d'] = "#00CC44"
  colors['g'] = "#FF8000"
  colors['f'] = "#FFCC00"
  colors['n'] = "#00B3B3"
  colors['o'] = "#A6A6A6"
  colors['r'] = "#FF0000"
  colors['s'] = "#6A5ACD"
  colors['m'] = "#FF6633"
  colors['w'] = "#7fffd4"

  pie_order = ('a','r','b','m','g','f','o','d','s','n','w')

  # Initialize in the 'other' state
  action_start = 0
  action_type = 'o'

  # Ready stdin for reading a single key
  stdin_state = ready_stdin()

  actions = defaultdict(list)
  while True:
    key = read_key(*stdin_state)
    curr_time = time.time() - time_delta

    if key == 'q':
      # Finish the current action
      actions[action_type].append((action_start, curr_time))

      # Summarize all of the actions
      totals = ()
      used_labels = ()
      used_colors = ()
      for key in pie_order:
        if key in actions:
          segments = actions[key]

          total = 0
          for beg, end in segments:
            total = total + (end - beg)
          totals = totals + (total,)

          print ''
          print '%s (%f seconds)' % (labels[key], total)
          print segments

          used_labels = used_labels + (labels[key],)
          used_colors = used_colors + (colors[key],)

      # Attempt to create a pie chart using pyplot
      try:
        import matplotlib.pyplot as plt
        plt.pie(totals, labels=used_labels, colors=used_colors, \
          autopct='%1.1f%%', shadow=True)
        plt.axis('equal')
        plt.show()
      except:
        print 'WARNING: Could not import pyplot'

      # Exit the while loop
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
      if key not in labels:
        print "WARNING: Unrecognized key, '%s'; defaulting to 'Other'" % key
        key = 'o'

      if print_progress:
        print '%s at %f seconds' % (labels[key], curr_time)

      if action_type != key:
        actions[action_type].append((action_start, curr_time))
        action_type = key
        action_start = curr_time

  # Put stdin back to normal before exiting
  restore_stdin(*stdin_state)

  return actions

if __name__ == "__main__":
  start()
