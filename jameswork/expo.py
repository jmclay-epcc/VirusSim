import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, bottom=0.35)

ax.set_xlim([0, 300])
ax.set_ylim([0, 105])

plt.xlabel('Distance from centre of infected player (unit)')
plt.ylabel('Chance of being infected (%)')
plt.title('Infection chance curves')
plt.grid(True)

M = 100
im = 0.5
I = 0.5
X = np.linspace(0, M, M+1)
k = ((np.square(((I+(I - im + 0.5))/2)-0.5)/1.25) + 0.05) * (150/M)
x0 = (0.8*M*(((I+(I - im + 0.5))/2))) + 0.1*M
Y =  100 / (1 + np.exp(k*(X-x0)))

line, = ax.plot(X, Y, lw=3, color="purple")

axMaxRange = plt.axes([0.25, 0.2, 0.6, 0.03])
sMaxRange = Slider(axMaxRange, 'Infectious Range', 1, 300.0, valinit=M)

axInfStrength = plt.axes([0.25, 0.12, 0.6, 0.03])
sInfStrength = Slider(axInfStrength, 'Infection Strength', 0.01, 1.0, valinit=I)

axImmunity = plt.axes([0.25, 0.04, 0.6, 0.03])
sImmunity = Slider(axImmunity, 'Immunity', 0.01, 1.0, valinit=im)

def update(val):
    M = int(sMaxRange.val)
    im = sImmunity.val
    I = sInfStrength.val
    X = np.linspace(0, M, M+1)
    k = ((np.square(((I+(I - im + 0.5))/2)-0.5)/1.25) + 0.05) * (150/M)
    x0 = (0.8*M*(((I+(I - im + 0.5))/2))) + 0.1*M
    Y =  100 / (1 + np.exp(k*(X-x0)))
    line.set_data(X, Y)
    ax.autoscale_view()
    fig.canvas.draw_idle()

sMaxRange.on_changed(update)
sInfStrength.on_changed(update)
sImmunity.on_changed(update)

plt.show()
