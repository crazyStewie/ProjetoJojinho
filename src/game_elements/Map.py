import math
from pymunk.vec2d import Vec2d
from src.utils import AngleHelper


class Map:
    def __init__(self):
        self.crossings = []
        self.streets = []
        self.STREET_WIDTH = 75
        self.SIDEWALK_WIDTH = 100
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
        sidewalk_borders = []
        for edge in self.streets:
            street_direction = (Vec2d(self.crossings[edge[1]]) - Vec2d(self.crossings[edge[0]])).normalized()
            normal_direction = street_direction.rotated_degrees(90)
            sidewalk_borders.append((self.crossings[edge[0]]+normal_direction*self.SIDEWALK_WIDTH, street_direction))
            sidewalk_borders.append((self.crossings[edge[0]]-normal_direction*self.SIDEWALK_WIDTH, street_direction))
        intersections = []
        for border_index in range(len(sidewalk_borders)):
            for border2_index in range(len(sidewalk_borders)):
                if border2_index <= border_index:
                    continue
                p1 = sidewalk_borders[border_index][0]
                v1 = sidewalk_borders[border_index][1]
                p2 = sidewalk_borders[border2_index][0]
                v2 = sidewalk_borders[border2_index][1]
                if abs(v1.x * v2.y - v2.x * v1.y - 0) > 1e-3:
                    lambda2 = (v1.y * (p2[0] - p1[0]) - v1.x * (p2[1] - p1[1])) / (v1.x * v2.y - v2.x * v1.y)
                    intersections.append((p2[0] + v2.x*lambda2, p2[1] + v2.y*lambda2))
        angles = []
        for i in range(len(self.crossings)):
            angles += [[]]
        for crossing_index in range(len(self.crossings)):
            crossing_angles = []
            for edge in self.streets:
                if crossing_index in edge:
                    crossing_angles.append(Vec2d(self.crossings[edge[(edge.index(crossing_index)+1) % 2]][0] -
                                                 self.crossings[crossing_index][0],
                                           self.crossings[edge[(edge.index(crossing_index)+1) % 2]][1] -
                                                 self.crossings[crossing_index][1]).angle_degrees)
            crossing_angles.sort()
            for i in range(len(crossing_angles)):
                angles[crossing_index].append(AngleHelper.angle_to_positive_degrees(
                    crossing_angles[(i+1) % len(crossing_angles)] - crossing_angles[i]))
        used_crossings = []
        for i in range(len(intersections)):
            used_crossings += [False]
        for crossing_index in range(len(self.crossings)):
            temp = []
            for intersection in intersections:
                for angle in angles[crossing_index]:
                    if (abs(Vec2d(intersection).get_distance(Vec2d(self.crossings[crossing_index])) -
                            self.SIDEWALK_WIDTH/math.sin(math.pi/180*angle/2)) < 1e-3 or
                        abs(Vec2d(intersection).get_distance(Vec2d(self.crossings[crossing_index])) -
                            self.SIDEWALK_WIDTH/math.cos(math.pi/180*angle/2)) < 1e-3) and \
                            not used_crossings[intersections.index(intersection)]:
                        used_crossings[intersections.index(intersection)] = True
                        temp.append(((Vec2d(intersection) - Vec2d(self.crossings[crossing_index])).angle,
                                     intersection))
                        break
            temp.sort()
            for i in range(len(temp)):
                self.sidewalk_crossings.append(temp[i][1])
            for i in range(len(temp)):
                if i < len(temp) - 1:
                    self.sidewalks.append((self.sidewalk_crossings.index(temp[i][1]),
                                           self.sidewalk_crossings.index(temp[i][1])+1))
                else:
                    self.sidewalks.append((self.sidewalk_crossings.index(temp[i][1]),
                                           self.sidewalk_crossings.index(temp[i][1]) + 1 - len(temp)))
        candidates = []
        for i in range(len(self.streets)):
            candidates += [[]]
        for edge_index in range(len(self.streets)):
            street_direction = (Vec2d(self.crossings[self.streets[edge_index][1]]) -
                                Vec2d(self.crossings[self.streets[edge_index][0]])).normalized()
            for crossing in self.sidewalk_crossings:
                if abs((street_direction.dot(Vec2d(crossing) - Vec2d(self.crossings[self.streets[edge_index][0]])) *
                        street_direction + Vec2d(self.crossings[self.streets[edge_index][0]])).get_distance(crossing) -
                       self.SIDEWALK_WIDTH) < 1e-3 and \
                        ((street_direction.dot(Vec2d(crossing) -
                                               Vec2d(self.crossings[self.streets[edge_index][0]])) > 0 and
                          street_direction.dot(Vec2d(crossing) -
                                               Vec2d(self.crossings[self.streets[edge_index][1]])) < 0) or (
                        street_direction.dot(Vec2d(crossing) -
                                             Vec2d(self.crossings[self.streets[edge_index][0]])) < 0 and
                        street_direction.dot(Vec2d(crossing) -
                                             Vec2d(self.crossings[self.streets[edge_index][1]])) > 0)):
                    normal_direction = street_direction.rotated_degrees(90)
                    angle = normal_direction.dot((Vec2d(crossing) - Vec2d(self.crossings[self.streets[edge_index][0]])))
                    candidates[edge_index].append((angle, self.sidewalk_crossings.index(crossing)))
            candidates[edge_index].sort()
            self.sidewalks.append((candidates[edge_index][0][1], candidates[edge_index][1][1]))
            self.sidewalks.append((candidates[edge_index][2][1], candidates[edge_index][3][1]))
