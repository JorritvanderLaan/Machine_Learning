import numpy as np
import matplotlib.pyplot as plt
from mnist import MNIST

mndata = MNIST('samples')
images, labels = mndata.load_training()
test, test_labels = mndata.load_testing()
test = np.array(test)/255
test_labels = np.array(test_labels)
images = np.array(images)[:1000]/255
labels = np.array(labels)[:1000]
train_data = np.concatenate([images, labels[:, None]], axis=1)

print(np.cov([1,2]))

digit = False
Data = np.random.choice([-1, 1], size=(10,200))



class Boltzmann_machine():
    def __init__(self,P,N,learning_rate,Data):
        self.P = P
        self.N = N
        self.eta = learning_rate

        self.Data = 0.99*Data

        self.means = np.zeros(shape=N)
        self.correlations = np.zeros(shape=(N, N))

        self.state = np.random.choice([-1, 1], size = N)

        self.weights = np.random.normal(size=(N,N))
        self.thetas = np.random.normal(size = N)

        self.clamped_means = np.sum(self.Data.T, axis=0)/P
        self.clamped_correlations = np.dot(self.Data, self.Data.T) * 1 / self.P

        #self.clamped_correlations = 0.99*(np.dot(Data.T,Data)/P)
        #self.clamped_correlations = (np.dot(Data.T,Data)-np.diag(1/(1-self.clamped_means**2))*1/P)
        self.C = np.cov(Data.T)

        self.free_energy = 0

    @staticmethod
    def sigmoid(x):
        return (np.exp(x)) / (np.exp(x) + 1)

    def sequential_dynamics(self):
        states = np.zeros(10)
        correlation = np.zeros((10,10))
        for i in range(500):
            n = np.random.choice(range(self.N))
            h = np.dot(self.weights[n,:], self.state) - self.weights[n, n] * self.state[n]
            probability = self.sigmoid(-self.state[n] * (h + self.thetas[n]))
            if probability > np.random.uniform(0,1):
                self.state[n] = -self.state[n]
            states += self.state
            correlation += np.outer(self.state, self.state)

        self.means = states/500
        self.correlations = correlation/500

    def mean_field(self):
        # C = self.clamped_correlations - np.outer(self.clamped_means,self.clamped_means)
        # C -= np.diag(C)
        # C += np.diag(1-self.clamped_means**2)
        #print(np.linalg.eig(C)[0])
        # C += 0.00001*np.identity(self.N)
        test = np.outer(self.clamped_means,self.clamped_means)
        self.weights = -np.linalg.inv(self.C+0.00001*np.identity(self.N))+np.diag(1/(1-(self.clamped_means**2)))
        self.thetas = np.arctanh(self.clamped_means) - np.dot(self.weights,self.clamped_means)

    def update_weights(self):
        self.sequential_dynamics()
        self.thetas += self.eta*(self.clamped_means-self.means)
        self.weights += self.eta*(self.clamped_correlations-self.correlations)

    def calculate_free_energy(self):
        a = -1/2*(np.dot(np.dot(self.weights,self.clamped_means), self.clamped_means))
        b = -np.dot(self.thetas,self.clamped_means)
        c = 1/2*(np.dot(1+self.clamped_means,np.log(1/2*(1+self.clamped_means))) + np.dot(1-self.clamped_means,np.log(1/2*(1-self.clamped_means))))
        self.free_energy = a+b+c




if not digit:
    Boltzmann_machine = Boltzmann_machine(200,10,0.1,Data)
    change_in_weights = []
    change_in_thetas = []
    for i in range(200):
        Boltzmann_machine.update_weights()
        change_in_weights.append(np.mean(np.abs(Boltzmann_machine.eta*(Boltzmann_machine.clamped_correlations-Boltzmann_machine.correlations))))
        change_in_thetas.append(np.mean(np.abs((Boltzmann_machine.eta*(Boltzmann_machine.clamped_means-Boltzmann_machine.means)))))

    iterations = np.arange(200)
    change_in_weights = np.array(change_in_weights)
    change_in_thetas = np.array(change_in_thetas)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.plot(iterations, change_in_weights, color='black', label='change in weights')
    ax1.plot(iterations, change_in_thetas, color='green', label='change in thetas')

    plt.legend()
    plt.show()
else:

    data_splits = []
    machines = []


    for i in range(10):
        data_splits.append(train_data[(train_data[:, -1] == i)])
        data_splits[i] = data_splits[i][:,:-1]
        data_splits[i][data_splits[i]<0.5] = -1
        data_splits[i][data_splits[i]!=-1] = 1


    for i in range(10):
        machines.append(Boltzmann_machine(data_splits[i][:,0].size, data_splits[i][0,:].size,0.01,data_splits[i]))

    machines[0].mean_field()
    # print(np.unique(machines[0].weights))
    machines[0].calculate_free_energy()
    # print(machines[0].free_energy)


    def classify_sample(test,label):
        score = -np.inf
        digit = -1
        for i,machine in enumerate(machines):
            machine.mean_field()
            machine.calculate_free_energy()
            new_score = (1/2*(np.dot(np.dot(machine.weights,test), test)+np.dot(machine.thetas,test)))
            new_score += machine.free_energy
            # print(machine.free_energy)
            print(new_score)
            if new_score > score:
                score = new_score
                digit = i
        print(digit)
        print(label)

    #print(test[0])
    for k in range(10):
        classify_sample(test[k],test_labels[k])

    # plt.imshow(machines[1].clamped_correlations)
    # plt.imshow(np.reshape(test[3],(28,28)))
    # plt.imshow(np.reshape(machines[0].clamped_means,(28,28)))






