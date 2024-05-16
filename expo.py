import numpy as np
import matplotlib.pyplot as plt

M = 200
I = 1

def sigmoid(x,M,I):
    k = (np.square(I-0.5)/1.25) + 0.05
    x0 = (0.6*M*(I)) + 0.2*M
    return 100 / (1 + np.exp(k*(x-x0)))

# Generate X values from -10 to 10
X = np.linspace(0, M, M+1)

# Calculate Y values using the sigmoid function
Y1 = sigmoid(X,M,0)
Y2 = sigmoid(X,M,0.25)
Y3 = sigmoid(X,M,0.5)
Y4 = sigmoid(X,M,0.75)
Y5 = sigmoid(X,M,1)

# Plot the graph
plt.plot(X, Y1, color="Red")
plt.plot(X, Y2, color="Blue")
plt.plot(X, Y3, color="Green")
plt.plot(X, Y4, color="Yellow")
plt.plot(X, Y5, color="Purple")
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Sigmoid Function')
plt.grid(True)
plt.show()
