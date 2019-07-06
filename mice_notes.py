#!/usr/bin/env python

#
#  Copyright 2019, Jack Poulson, Sandra Poulson
#  All rights reserved.
#
#  This file is part of mice_notes and is under the BSD 3-Clause License,
#  which can be found in the LICENSE file in the root directory, or at
#  http://opensource.org/licenses/BSD-2-Clause
#

from collections import defaultdict
import termios, fcntl, sys, os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time

labels = defaultdict()
labels['a'] = 'Allogrooming'
labels['b'] = 'Burrowing'
labels['d'] = 'Digging near mouse'  
labels['f'] = 'Fluffing own nest'
labels['n'] = 'Near'
labels['o'] = 'Other'
labels['r'] = 'Rearing/Climbing'
labels['s'] = 'Sniffing'
labels['m'] = 'TailShake/Aggressive'
labels['f'] = 'Paw Flicking'
labels['g'] = 'Paw Guarding'
labels['l'] = 'Paw Licking'

colors = defaultdict()
colors['a'] = "#0000E6"
colors['b'] = "#FF6666"
colors['d'] = "#00CC44"
colors['g'] = "#808080"
colors['f'] = "#FFCC00"
colors['n'] = "#00B3B3"
colors['o'] = "#FFFFFF"
colors['r'] = "#FF0000"
colors['s'] = "#6A5ACD"
colors['m'] = "#FF6633"
colors['f'] = "#FF0000"
colors['l'] = "#008080"

pie_order = ('a','r','b','m','o','d','s','n','f','g','l')

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
  
  'a': Allogrooming (grooming the other mouse)
  
  'b': Burrowing (rummaging under bedding or other mouse)
  
  'd': Digging near mouse

  'f': Fluffing own nest
  
  'n': Near (side-by-side)
  
  'r': Rearing (forepaws in air or against wall)
  
  's': Sniffing other
  
  'o': Other (blank state).

  'm': Pulling hair or aggressive behavior

  'f': Paw flicking

  'g': Paw guarding

  'l': Paw licking

  Additionally, 'q' quits and 'p' pauses/unpauses the recording process.
  """
  time_delta = time.time()
  paused = False

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

          print('')
          print('{} ({} seconds)'.format(labels[key], total))
          print(segments)

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
        print('WARNING: Could not import pyplot')

      # Exit the while loop
      break

    elif key == ' ':
      if paused:
        pause_time = curr_time - pause_start
        time_delta = time_delta + pause_time
        paused = False
        print('Ended {} second pause'.format(pause_time))
      else:
        pause_start = curr_time
        paused = True
        print('Pausing')

    elif not paused:
      if key not in labels:
        print('WARNING: Unrecognized key, "{}"; defaulting to "Other"'.format(key))
        key = 'o'

      if print_progress:
        print('{} at {} seconds'.format(labels[key], curr_time))

      if action_type != key:
        actions[action_type].append((action_start, curr_time))
        action_type = key
        action_start = curr_time

  # Put stdin back to normal before exiting
  restore_stdin(*stdin_state)

  return actions

def make_eventplot_from_actions(actions, granularity=0.1, line_offset=0,
    line_length=2, line_width=2):
  """Plots an event plot by chunking each interval.

  Args:
    actions: The dictionary from keystrokes to event interval lists.
    granularity: The time span granularity for emitting repeated events.
    line_offset: The vertical offset of the events.
    line_length: The vertical height of the event bars.
    line_width: The horizontal width of the events.

  Returns:
    Dictionary from keystrokes to lists of event instances.
  """
  chunked_data = []
  chunked_colors = []
  chunked_colors = np.zeros([0, 3])
  linewidths = []
  lineoffsets = []
  linelengths = []
  chunked_actions = {}
  for action in actions:
    color_hex = colors[action]
    red, green, blue = bytearray.fromhex(color_hex[1:])
    color_row = [red / 255., green / 255., blue / 255.]
    chunked_colors = np.vstack([chunked_colors, color_row])
    linewidths.append(2)
    lineoffsets.append(0)
    linelengths.append(2)

    chunked_actions[action] = []
    for interval in actions[action]:
      for time in np.arange(interval[0], interval[1], granularity): 
        chunked_actions[action].append(time)
    print(chunked_actions[action])
    chunked_data.append(chunked_actions[action])

  plt.eventplot(chunked_data, colors=chunked_colors, lineoffsets=lineoffsets,
      linewidths=linewidths, linelengths=linelengths)
  plt.show() 

  return chunked_actions

if __name__ == "__main__":
  actions = start()
  granularity = 0.1
  line_offset = 0
  line_length = 2
  line_width = 3
  chunked_actions = make_eventplot_from_actions(
      actions, granularity=granularity, line_offset=line_offset,
      line_length=line_length, line_width=line_width)
