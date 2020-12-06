import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    data = {'a': np.arange(50),
            'c': np.random.randint(0, 50, 50),
            'd': np.random.randn(50)}
    data['b'] = data['a'] + 10 * np.random.randn(50)
    data['d'] = np.abs(data['d']) * 100

    # plt.plot('a', 'b', c='c', s='d', data=data)

    # plt.plot(data["a"], data["b"], 'ro')
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.axis([0, 6, 0, 20])

    plt.xlabel('entry a')
    plt.ylabel('entry b')
    plt.show()
