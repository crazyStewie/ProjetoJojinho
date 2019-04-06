from pymunk.vec2d import Vec2d
from src.utils import AngleHelper
import pymunk


class Map:
    def __init__(self):
        self.crossings = []
        self.streets = []
        self.STREET_WIDTH = 50
        self.SIDEWALK_WIDTH = 60
        self.sidewalk_crossings = []
        self.sidewalks = []
        self.distances = []
        self.spawn_positions = []
        self.back_sprite = None
        self.front_sprite = None
        self.streets_length = []
        self.sidewalks_length = []
        self.collision_vertices = []
        self.collision_edges = []
        self.col_body = None
        self.col_shapes = []
        self.spawn_positions = [(100, 100), (150, 100), (200, 100), (250, 100)]
        self.spawn_rotations = [0, 0, 0, 0]

    def generate_body(self):
        self.col_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        for edge in self.collision_edges:
            self.col_shapes += [pymunk.shapes.Segment(self.col_body,
                                                      Vec2d(self.collision_vertices[edge[0]]),
                                                      Vec2d(self.collision_vertices[edge[1]]), 8)]
        for cvertex in self.collision_vertices:
            self.col_shapes += [pymunk.shapes.Circle(self.col_body, 8, cvertex)]

    def generate_matrix(self):
        self.distances.clear()
        for i in range(len(self.sidewalk_crossings)):
            self.distances += [[]]
        for i in range(len(self.sidewalk_crossings)):
            for j in range(len(self.sidewalk_crossings)):
                self.distances[i].append(-1)

        for i in range(len(self.sidewalk_crossings)):
            self.distances[i][i] = 0
        for edge in self.sidewalks:
            self.distances[edge[0]][edge[1]] = self.distances[edge[1]][edge[0]] = \
                Vec2d(self.sidewalk_crossings[edge[0]]).get_distance(Vec2d(self.sidewalk_crossings[edge[1]]))

        for k in range(len(self.sidewalk_crossings)):
            for i in range(len(self.sidewalk_crossings)):
                for j in range(len(self.sidewalk_crossings)):
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

    def calculate_lengths(self):
        self.streets_length.clear()
        for street in self.streets:
            self.streets_length.append((Vec2d(self.crossings[street[0]]) - Vec2d(self.crossings[street[1]])).length)
        self.sidewalks_length.clear()
        for sidewalk in self.sidewalks:
            self.sidewalks_length.append((Vec2d(self.sidewalk_crossings[sidewalk[0]]) -
                                          Vec2d(self.sidewalk_crossings[sidewalk[1]])).length)
    
    def calculate_internal_variables(self):
        self.generate_sidewalks()
        self.generate_matrix()
        self.calculate_lengths()

    def get_street_direction(self, street_index):
        if street_index >= len(self.streets):
            return
        return (Vec2d(self.crossings[self.streets[street_index][1]]) -
                Vec2d(self.crossings[self.streets[street_index][0]])).normalized()

    def get_sidewalk_direction(self, sidewalk_index):
        if sidewalk_index >= len(self.sidewalks):
            return
        return (Vec2d(self.sidewalk_crossings[self.sidewalks[sidewalk_index][1]]) -
                Vec2d(self.sidewalk_crossings[self.sidewalks[sidewalk_index][0]])).normalized()

    def street_first_crossing_index(self, street):
        return self.crossings.index(self.crossings[self.streets[street][0]])

    def street_second_crossing_index(self, street):
        return self.crossings.index(self.crossings[self.streets[street][1]])

    def sidewalk_first_crossing_index(self, sidewalk):
        return self.sidewalk_crossings.index(self.sidewalk_crossings[self.sidewalks[sidewalk][0]])

    def sidewalk_second_crossing_index(self, sidewalk):
        return self.sidewalk_crossings.index(self.sidewalk_crossings[self.sidewalks[sidewalk][1]])

    def street_first_crossing(self, street):
        return self.crossings[self.streets[street][0]]

    def street_second_crossing(self, street):
        return self.crossings[self.streets[street][1]]

    def sidewalk_first_crossing(self, sidewalk):
        return self.sidewalk_crossings[self.sidewalks[sidewalk][0]]

    def sidewalk_second_crossing(self, sidewalk):
        return self.sidewalk_crossings[self.sidewalks[sidewalk][1]]

    def draw_back(self):
        pass

    def draw_front(self):
        pass
