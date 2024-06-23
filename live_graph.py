from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import random
 
# initial data
x = [1]
y = [random.randint(1,10)]
 
# creating the first plot and frame
fig, ax = plt.subplots()
graph = ax.plot(x,y,color = 'g')[0]
plt.ylim(0,10)
print(x)

# updates the data and graph
def update(frame):
    global graph
 
    # updating the data
    x.append(x[-1] + 1)
    print(x)
    y.append(random.randint(1,10))
    print(y)
    # creating a news graph or updating the graph
    graph.set_xdata(x)
    graph.set_ydata(y)
    plt.xlim(x[0], x[-1])
 
anim = FuncAnimation(fig, update)

plt.show()