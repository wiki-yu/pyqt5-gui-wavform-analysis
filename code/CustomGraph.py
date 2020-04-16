import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation

class CustomGraph(animation.TimedAnimation):

    def __init__(self):

        self.n = np.linspace(0, 1000, 1001)
        self.y = 1.5 + np.sin(self.n/20)
        #self.y = np.zeros(self.n.size)

        # The window
        self.fig = plt.figure()
        ax1 = self.fig.add_subplot(1, 2, 1)
        self.mngr = plt.get_current_fig_manager()
        self.mngr.window.setGeometry(50,100,2000, 800)

        # ax1 settings
        ax1.set_xlabel('time')
        ax1.set_ylabel('raw data')
        self.line1 = Line2D([], [], color='blue')
        ax1.add_line(self.line1)
        ax1.set_xlim(0, 1000)
        ax1.set_ylim(0, 4)
        animation.TimedAnimation.__init__(self, self.fig, interval=20, blit=True)

    def _draw_frame(self, framedata):
        i = framedata
        print(i)

        self.line1.set_data(self.n[ 0 : i ], self.y[ 0 : i ])

        self._drawn_artists = [self.line1]

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1]
        for l in lines:
            l.set_data([], [])

    def showMyAnimation(self):
        plt.show()
