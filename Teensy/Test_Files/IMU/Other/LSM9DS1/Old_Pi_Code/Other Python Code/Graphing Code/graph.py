# ---------------------------------------------------------------------
# Last Modified:
#   9-12-2017
# Description:
#   This program reads data from a csv file and graphs it in 1 second
#   intervals.
# ---------------------------------------------------------------------

# ---------------------- Import required libraries --------------------
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ---------------------- Start Program --------------------------------

plt.close('all')
win = 200  # window length
filename = "/home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Pi_Data_v2a.csv"
fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=True)
fig.subplots_adjust(hspace=0)
plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)


def animate(i):
    graph_data = open(filename, 'r').read()
    lines = graph_data.split("\n")
    ts = []
    xs = []
    ys = []
    zs = []
    for line in lines:
        if len(line) > 0:
            parts = line.split(",")
            if len(parts) == 4:
                ts.append(parts[0])
                xs.append(parts[1])
                ys.append(parts[2])
                zs.append(parts[3])
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax1.plot(ts[-win:-1], xs[-win:-1], color='r')
    ax2.plot(ts[-win:-1], ys[-win:-1], color='b')
    ax3.plot(ts[-win:-1], zs[-win:-1], color='k')


ani = animation.FuncAnimation(fig, animate, interval=1000)
mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
# mng.full_screen_toggle()
plt.show()
