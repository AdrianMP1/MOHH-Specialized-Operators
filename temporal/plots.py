import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Create a figure
fig = plt.figure(figsize=(10, 5))

# Define the grid layout with 2 row and 2 columns (2 columns total for positioning)
gs = gridspec.GridSpec(2, 2, width_ratios=[2, 1])

# Create the first subplot on the left, taking up all the space on the left
ax1 = fig.add_subplot(gs[:, 0])  # Spans all rows of the first column

# Create the second subplot at the top right
ax2 = fig.add_subplot(gs[0, 1])  # Top right, first part of the right side

# Create the third subplot at the bottom right
ax3 = fig.add_subplot(gs[1, 1])  # Bottom right, second part of the right side

# Example data and plots for demonstration
ax1.plot([0, 1, 2], [10, 20, 10], label='Left Plot')
ax1.set_title('Left Subplot')
ax1.legend()

ax2.plot([0, 1, 2], [3, 2, 5], label='Top Right Plot')
ax2.set_title('Top Right Subplot')
ax2.legend()

ax3.plot([0, 1, 2], [4, 7, 1], label='Bottom Right Plot')
ax3.set_title('Bottom Right Subplot')
ax3.legend()

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()
