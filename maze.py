# author: jiangliqi
# Thursday 14/11/2019
import re
import numpy as np
import copy
from collections import defaultdict


class MazeError(Exception):
    def __init__(self, message):
        self.message = message
        print(message)


class Maze:
    def __init__(self, filename):
        self.filename = filename
        file = open(self.filename, 'r')
        self.grid = []
        for line in file.readlines():
            if line.strip():
                self.grid.append(''.join(line.strip().split()))
        self.x = len(self.grid)
        self.y = len(self.grid[0])
        for i in self.grid:
            # does not only contain (0,1,2,3) besides spaces or have different number of digits
            if re.compile(r'[0,1,2,3]+$').match(i) is None or len(i) != self.y:
                raise MazeError('Incorrect input.')
        # too many x or too many y
        if not 2 <= self.x <= 41 or not 2 <= self.y <= 31:
            raise MazeError('Incorrect input.')
        # Input does not represent a maze
        if re.compile(r'[0,1]+$').match(self.grid[-1]) is None:
            raise MazeError('Input does not represent a maze.')
        for i in range(self.x):
            if self.grid[i][self.y-1] not in ['0', '2']:
                raise MazeError('Input does not represent a maze.')
        # generate a 2 dimension array that replace each point with 4 digits
        self.grid_array = np.zeros((2 * self.x, 2 * self.y), np.int)
        for i in range(self.x):
            for j in range(self.y):
                if self.grid[i][j] == '0':
                    self.grid_array[2 * i][2 * j] = 1
                    self.grid_array[2 * i + 1][2 * j] = 0
                    self.grid_array[2 * i][2 * j + 1] = 0
                    self.grid_array[2 * i + 1][2 * j + 1] = 0
                if self.grid[i][j] == '1':
                    self.grid_array[2 * i][2 * j] = 1
                    self.grid_array[2 * i + 1][2 * j] = 0
                    self.grid_array[2 * i][2 * j + 1] = 1
                    self.grid_array[2 * i + 1][2 * j + 1] = 0
                if self.grid[i][j] == '2':
                    self.grid_array[2 * i][2 * j] = 1
                    self.grid_array[2 * i + 1][2 * j] = 1
                    self.grid_array[2 * i][2 * j + 1] = 0
                    self.grid_array[2 * i + 1][2 * j + 1] = 0
                if self.grid[i][j] == '3':
                    self.grid_array[2 * i][2 * j] = 1
                    self.grid_array[2 * i + 1][2 * j] = 1
                    self.grid_array[2 * i][2 * j + 1] = 1
                    self.grid_array[2 * i + 1][2 * j + 1] = 0
        self.gate = []
        self.path = []
        self.nb_of_gate = self.nb_of_gate()
        self.nb_of_wall = self.nb_of_wall()
        self.nb_of_inner_point = self.nb_of_inner_point()
        self.nb_of_accessible_area = self.nb_of_accessible_area()
        self.nb_of_culdesac = self.nb_of_culdesac()
        self.nb_of_path = self.nb_of_path()

    def analyse(self):
        # judge the number of gates
        if self.nb_of_gate == 0:
            print('The maze has no gate.')
        elif self.nb_of_gate == 1:
            print('The maze has a single gate.')
        else:
            print('The maze has', self.nb_of_gate, 'gates.')
        # judge the number of sets of walls
        if self.nb_of_wall == 0:
            print('The maze has no wall.')
        elif self.nb_of_wall == 1:
            print('The maze has walls that are all connected.')
        else:
            print('The maze has', self.nb_of_wall, 'sets of walls that are all connected.')
        # judge the number of inaccessible inner point
        if self.nb_of_inner_point == 0:
            print('The maze has no inaccessible inner point.')
        elif self.nb_of_inner_point == 1:
            print('The maze has a unique inaccessible inner point.')
        else:
            print('The maze has', self.nb_of_inner_point, 'inaccessible inner points.')
        # judge the number of accessible areas
        if self.nb_of_accessible_area == 0:
            print('The maze has no accessible area.')
        elif self.nb_of_accessible_area == 1:
            print('The maze has a unique accessible area.')
        else:
            print('The maze has', self.nb_of_accessible_area, 'accessible areas.')
        # judge the number of sets of accessible cul-de-sac
        if self.nb_of_culdesac == 0:
            print('The maze has no accessible cul-de-sac.')
        elif self.nb_of_culdesac == 1:
            print('The maze has accessible cul-de-sacs that are all connected.')
        else:
            print('The maze has', self.nb_of_culdesac, 'sets of accessible cul-de-sacs that are all connected.')
        if self.nb_of_path == 0:
            print('The maze has no entry-exit path with no intersection not to cul-de-sacs.')
        elif self.nb_of_path == 1:
            print('The maze has a unique entry-exit path with no intersection not to cul-de-sacs.')
        else:
            print('The maze has', self.nb_of_path, 'entry-exit paths with no intersections not to cul-de-sacs.')

    # number of gate
    def nb_of_gate(self):
        count_gate = 0
        for i in range(0, 2 * self.y - 1):
            if self.grid_array[0][i] == 0:
                self.gate.append((0, i))
                count_gate += 1
        for i in range(0, 2 * self.y - 1):
            if self.grid_array[2 * self.x - 2][i] == 0:
                self.gate.append((2 * self.x - 2, i))
                count_gate += 1
        for i in range(0, 2 * self.x - 1):
            if self.grid_array[i][0] == 0:
                self.gate.append((i, 0))
                count_gate += 1
        for i in range(0, 2 * self.x - 1):
            if self.grid_array[i][2 * self.y - 2] == 0:
                self.gate.append((i, 2 * self.y - 2))
                count_gate += 1
        return count_gate

    # number of sets of walls, point_list contains all the point whose value is 1, shape_list is used to pop
    def nb_of_wall(self):
        count = 0
        for i in self.colour(1):
            if len(i) > 1:
                count += 1
        return count

    # number of inaccessible inner points, inner_point_list contains all the points during each loop
    def nb_of_inner_point(self):
        count = 0
        set_of_inner_point = self.set_of_inner_point()
        for i in set_of_inner_point:
            for j in i:
                if j[0] % 2 == 1 and j[1] % 2 == 1:
                    count += 1
        return count

    def nb_of_accessible_area(self):
        count = len(self.colour(0)) - len(self.set_of_inner_point())
        return count

    def nb_of_culdesac(self):
        self.culdesac_path()
        count = len(self.colour(-1))
        return count

    def nb_of_path(self):
        count_path = 0
        set_of_path = self.colour(0)
        for i in self.set_of_inner_point():
            if i in set_of_path:
                set_of_path.remove(i)
        direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for i in set_of_path:
            label = 0
            for j in i:
                count = 0
                for d in direction:
                    i1, j1 = d[0]+j[0], d[1]+j[1]
                    if i1 in range(0, 2 * self.x - 1) and j1 in range(0, 2 * self.y - 1) and self.grid_array[i1, j1] == 0:
                        count += 1
                if count > 2:
                    label = 1
                    break
            if label == 0:
                self.path.append(i)
                count_path += 1
        return count_path

    # from the culdesac generate the culdesac path
    def culdesac_path(self):
        culdesac = self.culdesac()
        for c in culdesac:
            self.grid_array[c[0], c[1]] = -1
            self.cul_path(c[0], c[1])

    # generate the (x, y) of each culdesac
    def culdesac(self):
        culdesac = []
        set_of_zero = self.colour(0)
        for i in self.set_of_inner_point():
            if i in set_of_zero:
                set_of_zero.remove(i)
        for i in set_of_zero:
            for j in i:
                if j[0] in range(1, 2 * self.x - 2) and j[1] in range(1, 2 * self.y - 2):
                    if self.grid_array[j[0]-1, j[1]-1] and self.grid_array[j[0]-1, j[1]+1] and self.grid_array[j[0]+1, j[1]-1] and self.grid_array[j[0]+1, j[1]+1]:
                        direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                        count = 0
                        for d in direction:
                            i1, j1 = j[0] + d[0], j[1] + d[1]
                            if self.grid_array[i1][j1] == 0:
                                count += 1
                        if count == 1:
                            culdesac.append(j)
        return culdesac

    # recursion
    def cul_path(self, i, j):
        direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in direction:
            i1, j1 = i+d[0], j+d[1]
            if i1 in range(0, 2*self.x-1) and j1 in range(0, 2*self.y-1) and self.grid_array[i1, j1] == 0:
                count = 0
                for di in direction:
                    i2, j2 = i1+di[0], j1+di[1]
                    if i2 in range(0, 2*self.x-1) and j2 in range(0, 2*self.y-1) and self.grid_array[i2, j2] == 0:
                        count += 1
                if count <= 1:
                    self.grid_array[i1, j1] = -1
                    self.cul_path(i1, j1)
                else:
                    break

    def set_of_inner_point(self):
        set_of_inner_point = []
        for i in self.colour(0):
            label = 0
            for j in i:
                if j[0] in [0, 2 * self.x - 2] or j[1] in [0, 2 * self.y - 2]:
                    label = 1
                    break
            if label == 0:
                set_of_inner_point.append(i)
        return set_of_inner_point

    def colour(self, value):
        colour = 2
        direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        grid_array_copy = copy.deepcopy(self.grid_array)
        shape_list = []
        for i in range(2 * self.x - 1):
            for j in range(2 * self.y - 1):
                if grid_array_copy[i][j] == value:
                    point_list = [(i, j)]
                    all_point_list = [(i, j)]
                    grid_array_copy[i][j] = colour
                    while point_list:
                        (i0, j0) = point_list.pop()
                        for d in direction:
                            i1, j1 = i0 + d[0], j0 + d[1]
                            if (i1, j1) not in all_point_list and 0 <= i1 < 2 * self.x - 1 and 0 <= j1 < 2 * self.y - 1 and grid_array_copy[i1][j1] == value:
                                grid_array_copy[i1][j1] = colour
                                point_list.append((i1, j1))
                                all_point_list.append((i1, j1))
                    shape_list.append(all_point_list)
        return shape_list

    def display(self):
        tex_filename = self.filename.split('.')[0]+'.tex'
        texfile = open(tex_filename, 'w')
        head = ['\\documentclass[10pt]{article}\n',
                '\\usepackage{tikz}\n',
                '\\usetikzlibrary{shapes.misc}\n',
                '\\usepackage[margin=0cm]{geometry}\n',
                '\\pagestyle{empty}\n',
                '\\tikzstyle{every node}=[cross out, draw, red]\n',
                '\n',
                '\\begin{document}\n',
                '\n',
                '\\vspace*{\\fill}\n',
                '\\begin{center}\n',
                '\\begin{tikzpicture}[x=0.5cm, y=-0.5cm, ultra thick, blue]\n']
        border = ['\\end{tikzpicture}\n',
                  '\\end{center}\n',
                  '\\vspace*{\\fill}\n',
                  '\n',
                  '\\end{document}\n']
        texfile.writelines(head)
        texfile.writelines(self.draw_wall())
        texfile.writelines(self.draw_pillar())
        texfile.writelines(self.draw_inner_points())
        texfile.writelines(self.draw_path())
        texfile.writelines(border)

    def draw_wall(self):
        wall_line = ['% Walls\n']
        for i in range(0, 2*self.x-1, 2):
            j = 0
            j1 = 1
            while j1 < 2*self.y-1:
                if self.grid_array[i][j] == 1 and self.grid_array[i][j1] == 1:
                    j1 += 1
                else:
                    if j1//2 != j//2:
                        line = '    \\draw ('+str(j//2)+','+str(i//2)+') -- ('+str(j1//2)+','+str(i//2)+');\n'
                        wall_line.append(line)
                    j = j1 + 1
                    j1 = j + 1
            if j1//2 != j//2:
                line = '    \\draw ('+str(j//2)+','+str(i//2)+') -- ('+str(j1//2)+','+str(i//2)+');\n'
                wall_line.append(line)
        for j in range(0, 2 * self.y - 1, 2):
            i = 0
            i1 = 1
            while i1 < 2 * self.x - 1:
                if self.grid_array[i][j] == 1 and self.grid_array[i1][j] == 1:
                    i1 += 1
                else:
                    if i1 // 2 != i // 2:
                        line = '    \\draw (' + str(j//2) + ',' + str(i//2) + ') -- (' + str(j//2) + ',' + str(i1//2) + ');\n'
                        wall_line.append(line)
                    i = i1 + 1
                    i1 = i + 1
            if i1//2 != i//2:
                line = '    \\draw ('+str(j//2)+','+str(i//2)+') -- ('+str(j//2)+','+str(i1//2)+');\n'
                wall_line.append(line)
        return wall_line

    def draw_pillar(self):
        pillar_line = ['% Pillars\n']
        pillar_point = []
        for i in self.colour(1):
            if len(i) == 1:
                pillar_point.extend(i)
        for x in range(0, 2*self.x-1):
            for y in range(0, 2*self.y-1):
                if (x, y) in pillar_point:
                    line = '    \\fill[green] ('+str(y//2)+','+str(x//2)+') circle(0.2);\n'
                    pillar_line.append(line)
        return pillar_line

    def draw_inner_points(self):
        inner_point_line = ['% Inner points in accessible cul-de-sacs\n']
        inner_point = []
        for i in self.colour(-1):
            inner_point.extend(i)
        for x in range(1, 2*self.x-2, 2):
            for y in range(1, 2*self.y-2, 2):
                if (x, y) in inner_point:
                    line = '    \\node at ('+str(y/2)+','+str(x/2)+') {};\n'
                    inner_point_line.append(line)
        return inner_point_line

    def draw_path(self):
        path_line = ['% Entry-exit paths without intersections\n']
        x_y_list_horizontal = []
        x_y_list_vertical = []
        h_dict = {}
        v_dict = {}
        for i in self.path:
            x_list = [j[0] for j in i]
            y_list = [j[1] for j in i]
            for x in range(min(x_list), max(x_list)+1):
                y = min(y_list)
                y1 = y + 1
                while y1 <= max(y_list):
                    if (x, y) in i and (x, y1) in i:
                        y1 += 1
                    else:
                        if y1 != y + 1:
                            x_y = [(y, x), (y1-1, x)]
                            x_y_list_horizontal.append(x_y)
                        y = y1
                        y1 = y + 1
                if y1 != y + 1:
                    x_y = [(y, x), (y1-1, x)]
                    x_y_list_horizontal.append(x_y)
            for y in range(min(y_list), max(y_list)+1):
                x = min(x_list)
                x1 = x + 1
                while x1 <= max(x_list):
                    if (x, y) in i and (x1, y) in i:
                        x1 += 1
                    else:
                        if x1 != x + 1:
                            x_y = [(y, x), (y, x1-1)]
                            x_y_list_vertical.append(x_y)
                        x = x1
                        x1 = x + 1
                if x1 != x + 1:
                    x_y = [(y, x), (y, x1-1)]
                    x_y_list_vertical.append(x_y)
        x_y_list_horizontal = self.edge(x_y_list_horizontal)
        x_y_list_vertical = self.edge(x_y_list_vertical)
        for i in x_y_list_horizontal:
            h_dict.update({i[0]: i[1]})
        for i in x_y_list_vertical:
            v_dict.update({i[0]: i[1]})
        for x in range(-1, 2*self.x-2, 2):
            for y in range(-1, 2*self.y-2, 2):
                if (y, x) in h_dict.keys():
                    line = '    \\draw[dashed, yellow] ('+str(y/2)+','+str(x/2)+') -- ('+str(h_dict[(y, x)][0]/2)+','+str(h_dict[(y, x)][1]/2)+');\n'
                    path_line.append(line)
        for y in range(-1, 2*self.y-2, 2):
            for x in range(-1, 2*self.x-2, 2):
                if (y, x) in v_dict.keys():
                    line = '    \\draw[dashed, yellow] ('+str(y/2)+','+str(x/2)+') -- ('+str(v_dict[(y, x)][0]/2)+','+str(v_dict[(y, x)][1]/2)+');\n'
                    path_line.append(line)
        return path_line

    def edge(self, l):
        for i in range(len(l)):
            for j in range(0, 2):
                if l[i][j][0] == 0:
                    l[i][j] = (-1, l[i][j][1])
                if l[i][j][1] == 0:
                    l[i][j] = (l[i][j][0], -1)
                if l[i][j][0] == 2*self.y - 2:
                    l[i][j] = (2*self.y - 1, l[i][j][1])
                if l[i][j][1] == 2*self.x - 2:
                    l[i][j] = (l[i][j][0], 2*self.x - 1)
        return l


