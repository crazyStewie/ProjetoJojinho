from pymunk.vec2d import Vec2d
from src.utils import AngleHelper


class Map:
    def __init__(self):
        self.crossings = []
        self.streets = []
        self.STREET_WIDTH = 75
        self.SIDEWALK_WIDTH = 85
        self.sidewalk_crossings = []
        self.sidewalks = []
        self.distances = []

    def generate_matrix(self):
        self.distances.clear()
        for i in range(len(self.crossings)):
            self.distances += [[]]
        for i in range(len(self.crossings)):
            for j in range(len(self.crossings)):
                self.distances[i].append(-1)

        for i in range(len(self.crossings)):
            self.distances[i][i] = 0
        for edge in self.streets:
            self.distances[edge[0]][edge[1]] = self.distances[edge[1]][edge[0]] = \
                Vec2d(self.crossings[edge[0]]).get_distance(Vec2d(self.crossings[edge[1]]))

        for k in range(len(self.crossings)):
            for i in range(len(self.crossings)):
                for j in range(len(self.crossings)):
                    if self.distances[i][k] != -1 and self.distances[k][j] != -1:
                        if self.distances[i][k] + self.distances[k][j] < self.distances[i][j] or \
                                self.distances[i][j] == -1:
                            self.distances[i][j] = self.distances[i][k] + self.distances[k][j]

    def generate_sidewalks(self):
        self.sidewalk_crossings.clear()
        self.sidewalks.clear()
        vertices_streets = []
        for crossing_index in range(len(self.crossings)):
            vertex_street_directions = []
            for street in self.streets:
                if crossing_index in street:
                    vertex_street_directions.append(
                        ((Vec2d(self.crossings[street[(street.index(crossing_index) + 1) % 2]]) -
                          Vec2d(self.crossings[crossing_index])).normalized(), self.streets.index(street)))
            vertex_street_directions.sort(key=lambda obj: obj[0].angle)
            for direction_index in range(len(vertex_street_directions)):
                temp_vec = vertex_street_directions[direction_index][0].rotated(AngleHelper.angle_to_positive(
                    vertex_street_directions[direction_index][0].get_angle_between(
                        vertex_street_directions[(direction_index + 1) % len(vertex_street_directions)][0]))/2)
                temp_vec.length = self.SIDEWALK_WIDTH / \
                    (2 * abs(temp_vec.dot(vertex_street_directions[direction_index][0].perpendicular())))
                vertices_streets.append((Vec2d(self.crossings[crossing_index]) + temp_vec,
                                         vertex_street_directions[direction_index][1],
                                         vertex_street_directions[(direction_index + 1) %
                                                                  len(vertex_street_directions)][1], crossing_index))
        for element in vertices_streets:
            self.sidewalk_crossings.append((element[0].x, element[0].y))
        for element_index in range(len(vertices_streets)):
            if element_index < len(vertices_streets) - 1:
                if vertices_streets[element_index][3] == vertices_streets[element_index + 1][3]:
                    self.sidewalks.append((self.sidewalk_crossings.index(vertices_streets[element_index][0]),
                                           self.sidewalk_crossings.index(vertices_streets[element_index + 1][0])))
                elif element_index > 0:
                    if vertices_streets[element_index][3] == vertices_streets[element_index - 1][3]:
                        lower = element_index - 1
                        while lower > 0 and vertices_streets[lower][3] == vertices_streets[lower - 1][3]:
                            lower -= 1
                        if vertices_streets[lower][3] == vertices_streets[element_index][3]:
                            self.sidewalks.append((self.sidewalk_crossings.index(vertices_streets[element_index][0]),
                                                   self.sidewalk_crossings.index(vertices_streets[lower][0])))
            elif element_index > 0:
                if vertices_streets[element_index][3] == vertices_streets[element_index - 1][3]:
                    lower = element_index - 1
                    while lower > 0 and vertices_streets[lower][3] == vertices_streets[lower - 1][3]:
                        lower -= 1
                    if vertices_streets[lower][3] == vertices_streets[element_index][3]:
                        self.sidewalks.append((self.sidewalk_crossings.index(vertices_streets[element_index][0]),
                                               self.sidewalk_crossings.index(vertices_streets[lower][0])))
        for street_index in range(len(self.streets)):
            crossings = []
            for vertex_street in vertices_streets:
                if vertex_street[1] == street_index or vertex_street[2] == street_index:
                    crossings.append(vertex_street)
            street_direction = (Vec2d(self.crossings[self.streets[street_index][0]]) -
                                Vec2d(self.crossings[self.streets[street_index][1]])).normalized()
            if street_direction.perpendicular().dot(crossings[0][0] -
                                                    Vec2d(self.crossings[self.streets[street_index][0]])) * \
                    street_direction.perpendicular().dot(crossings[1][0] -
                                                         Vec2d(self.crossings[self.streets[street_index][0]])) > 0:
                self.sidewalks.append((self.sidewalk_crossings.index(crossings[0][0]),
                                       self.sidewalk_crossings.index(crossings[1][0])))
                self.sidewalks.append((self.sidewalk_crossings.index(crossings[2][0]),
                                       self.sidewalk_crossings.index(crossings[3][0])))
            elif street_direction.perpendicular().dot(crossings[0][0] -
                                                      Vec2d(self.crossings[self.streets[street_index][0]])) * \
                    street_direction.perpendicular().dot(crossings[2][0] -
                                                         Vec2d(self.crossings[self.streets[street_index][0]])) > 0:
                self.sidewalks.append((self.sidewalk_crossings.index(crossings[0][0]),
                                       self.sidewalk_crossings.index(crossings[2][0])))
                self.sidewalks.append((self.sidewalk_crossings.index(crossings[1][0]),
                                       self.sidewalk_crossings.index(crossings[3][0])))
            else:
                self.sidewalks.append((self.sidewalk_crossings.index(crossings[0][0]),
                                       self.sidewalk_crossings.index(crossings[3][0])))
                self.sidewalks.append((self.sidewalk_crossings.index(crossings[1][0]),
                                       self.sidewalk_crossings.index(crossings[2][0])))
