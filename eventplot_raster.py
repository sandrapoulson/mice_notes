"""
===========================================
Eventplot Raster for use with mice_notes.py
===========================================

An eventplot showing sequences of events with various line properties.
The plot is shown in both horizontal and vertical orientations.
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.rcParams['font.size'] = 8.0

exp0_behavior0 = []

exp1_behavior0 = []

exp2_behavior0 = []

behavior_events= [
  exp0_behavior0,
  exp1_behavior0,
  exp2_behavior0
]

# set different colors for each set of positions
colors1 = ['C{}'.format(i) for i in range(3)]

# set different line properties for each set of positions
# note that some overlap
lineoffsets1 = np.array([-15, 0, 15])
linelengths1 = [5, 5, 5]

# create a horizontal plot
plt.eventplot(behavior_events, colors=colors1,
              lineoffsets=lineoffsets1,
              linelengths=linelengths1)
plt.ylabel('')
plt.yticks([])

plt.show()
