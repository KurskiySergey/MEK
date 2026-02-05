import matplotlib.pyplot as plt
import time
import random
from collections import deque

plt.ion()  # Turn on interactive mode

# Use a deque to maintain a fixed-size window of data
data_points = deque([0] * 50, maxlen=50)
print(data_points)
fig, ax = plt.subplots()
line, = ax.plot(list(range(50)), list(data_points))
ax.set_ylim(0, 100)  # Set y-axis limit

for i in range(100):
    # Generate or acquire new data
    new_value = random.randint(0, 100)
    data_points.append(new_value)  # append left may be used depending on desired direction
    # Update the line object's data
    line.set_ydata(data_points)

    # Rescale axes if needed (optional)
    ax.relim()
    ax.autoscale_view(True, True, True)

    # Redraw the figure
    plt.draw()

    # Pause to allow time for the plot to be visualized and prevent a tight loop
    plt.pause(0.01)

plt.ioff()  # Turn off interactive mode (optional)
plt.show()  # Keep the final plot open
