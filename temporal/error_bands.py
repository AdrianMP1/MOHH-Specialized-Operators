

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    sns.set()

    x = np.linspace(0,30,30)

    y = np.sin(x/6)

    error = np.random.normal(0.5, 0.1, size=y.shape)

    plt.plot(x,y,c="k")
    plt.fill_between(x, y-error, y+error, alpha=0.2)
    plt.show()