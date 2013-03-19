from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
def Draw3dTrainSet(TrainSet,target):
    plt.ioff()
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    x = []
    y = []
    z = []
    for time in TrainSet:
        for item in TrainSet[time]:
            if item['status'] != target:
                x.append(item['h'][0])
                y.append(item['h'][1])
                z.append(item['h'][2])
            else:
                ax.scatter(item['h'][0], item['h'][1], item['h'][2], c='r')
        ax.scatter(x, y, z, c='b')
        plt.show()
