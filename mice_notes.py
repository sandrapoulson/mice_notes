#!/usr/bin/env python

# NOTE: This was copied from a Stack Overflow post
def read_key():
    """Waits for a single keypress on stdin.
    
    This is a silly function to call if you need to do it a lot because it has
    to store stdin's current setup, setup stdin for reading single keystrokes
    then read the single keystroke then revert stdin back after reading the
    keystroke.
    
    Returns the character of the key that was pressed (zero on
    KeyboardInterrupt which can happen when a signal gets handled)
    
    """
    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    attrs = list(attrs_save)
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON)
    attrs[1] &= ~termios.OPOST
    attrs[2] &= ~(termios.CSIZE | termios.PARENB)
    attrs[2] |= termios.CS8
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    try:
        ret = sys.stdin.read(1)
    except KeyboardInterrupt:
        ret = 0
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)

    return ret


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
    
    'o': Other (stop indicator or other unscored behavior).
    """
    import time
    from collections import defaultdict
    start_time = time.time()
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

    while True:
        key = read_key()
        curr_time = time.time() - start_time
        if print_progress:
            print 'Recorded %s after %f seconds' % (key, curr_time)
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
                print 'action: %s (total of %f seconds)' % (char, total)
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
        else:
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

            if action_type != key:
                actions[action_type].append((action_start, curr_time))
                action_type = key
                action_start = curr_time
