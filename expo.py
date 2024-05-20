import numpy as np
import matplotlib.pyplot as plt

M = 1000 # Max infectious range
I = 0.2 # Infection strength

def sigmoid(x,M,I):
    k = ((np.square(I-0.5)/1.25) + 0.05) * (150/M)
    x0 = (0.8*M*(I)) + 0.1*M
    return 100 / (1 + np.exp(k*(x-x0)))

# Generate X values from -10 to 10
X = np.linspace(0, M, M+1)

# Calculate Y values using the sigmoid function
Y1 = sigmoid(X,M,0)
Y2 = sigmoid(X,M,0.25)
Y3 = sigmoid(X,M,0.5)
Y4 = sigmoid(X,M,0.75)
Y5 = sigmoid(X,M,1)
Y = sigmoid(X,M,I)

# Plot the graph
plt.plot(X, Y1, color="Red")
plt.plot(X, Y2, color="Blue")
plt.plot(X, Y3, color="Green")
plt.plot(X, Y4, color="Yellow")
plt.plot(X, Y5, color="Purple")
plt.plot(X, Y, color="Black")
plt.xlabel('Distance from infected player (unit)')
plt.ylabel('Chance of being infected (%)')
plt.title('Infection chance curves')
plt.grid(True)
plt.show()
