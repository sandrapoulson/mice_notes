### mice_notes
A simple utility for recording a small selection of states of a mouse in a cage.

#### Running the program

The simplest way to run the program is via the command:

```
python mice_notes
```

which immediately starts the recording process. After recording has begun,
the following keys 

* 'a': Allogrooming (grooming the unconscious mouse)

* 'b': Burrowing (rummaging under bedding or other mouse)

* 'c': Climbing cage

* 'g': Grooming self

* 'n': Nesting behavior (bringing materials or building nest)

* 'r': Rearing (forepaws in air)

* 's': Sitting

* 'o': Other (blank state)

* 'q': Quit the recording process

* ' ': Pause/unpause the recording process

After quitting, if PyPlot is installed, a pie chart of the time spent in each
action is displayed. Furthermore, more advanced users may want to instead load
the `mice_notes` module within python (`import mice_notes`) so that the 
raw dictionary of action time segments can be returned. For example,

```
import mice_notes
first_video_actions = mice_notes.start()
second_video_actions = mice_notes.start()
```

would allow the data from a first video to be recorded in a dictionary named
`first_video`, and likewise for the second video. These dictionaries can then
be probed for the raw data of each action, such as

```
>>> first_video['o']
[(0, 0.29196596145629883), (1.7228410243988037, 3.185948133468628)]
```
