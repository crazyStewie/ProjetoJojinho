import math


class Map:
    def __init__(self):
        self.crossings = []
        self.streets = []
        self.STREET_WIDTH = 75
        self.distances = []

    def generate_matrix(self):
        for vertice in self.crossings:
            self.distances += [[]]
        for i in range(len(self.crossings)):
            for j in range(len(self.crossings)):
                self.distances[i].append(-1)
        for i in range(len(self.crossings)):
            self.distances[i][i] = 0
        for edge in self.streets:
            self.distances[edge[0]][edge[1]] = self.distances[edge[1]][edge[0]] = \
                math.sqrt((self.crossings[edge[0]][0]-self.crossings[edge[1]][0])**2 +
                          (self.crossings[edge[0]][1]-self.crossings[edge[1]][1])**2)

        for k in range(len(self.crossings)):
            for i in range(len(self.crossings)):
                for j in range(len(self.crossings)):
                    if self.distances[i][k] != -1 and self.distances[k][j] != -1:
                        if self.distances[i][k] + self.distances[k][j] < self.distances[i][j] or self.distances[i][j] == -1:
                            self.distances[i][j] = self.distances[i][k] + self.distances[k][j]
