import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0, 2*np.pi,400, endpoint =False)
x=400+300*np.cos(theta)
y=300+200*np.sin(theta)

plt.plot(x,y)
plt.gca().invert_yaxis()
plt.axis('equal')
plt.show()
