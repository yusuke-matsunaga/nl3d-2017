#! /usr/bin/env python3

### @file router.py
### @brief Router の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

from nl3d.v2017.point import Point
from nl3d.v2017.solution import Solution
from nl3d.v2017.dimension import Dimension

class Cell :

    def __init__(self, index, dimension) :
        self.__index = index
        self.__point = dimension.index_to_point(index)
        self.__adj_cell = [None for i in range(0, 6)]
        self.__label = 0
        self.__backtrace_info = [None for i in range(0, 6)]

    def set_adj_cell(self, dir_id, cell) :
        assert 0 <= dir_id < 6
        self.__adj_cell[dir_id] = cell

    def set_backtrace_info(self, dir_id, edge) :
        assert 0 <= dir_id < 6
        self.__backtrace_info[dir_id] = edge

    @property
    def index(self) :
        return self.__index

    @property
    def point(self) :
        return self.__point

    def adj_cell(self, dir_id) :
        assert 0 <= dir_id < 6
        return self.__adj_cell[dir_id]

    def backtrace_info(self, dir_id) :
        assert 0 <= dir_id < 6
        return self.__backtrace_info[dir_id]

class Edge :

    def __init__(self, from_cell, to_cell, bend_num, next_edge) :
        self._from = from_cell
        self._to = to_cell
        self._bend_num = bend_num
        self._next = next_edge


class RouteInfo :

    def __init__(self, routes) :
        nr = len(routes)
        assert nr >= 2
        start = routes[0]
        end = routes[nr - 1]
        self._start_point = start
        self._end_point = end
        self._points = [routes[i] for i in range(1, nr - 1)]

    def count_bends(self) :
        t_bend = 0
        n = len(self._points)
        if n > 0 :
            prev2_point = self._start_point
            prev1_point = self._points[0]
            for i in range(1, n) :
                point = self._points[i]
                if check_bend(prev2_point, prev1_point, point) :
                    t_bend += 1
                prev2_point = prev1_point
                prev1_point = point
            if check_bend(prev2_point, prev1_point, self._end_point) :
                t_bend += 1
        return t_bend

def check_bend(point1, point2, point3) :
    x1, y1, z1 = point1.xyz
    x2, y2, z2 = point2.xyz
    x3, y3, z3 = point3.xyz

    x_diff = False
    y_diff = False
    z_diff = False

    if x1 != x2 or x2 != x3 :
        x_diff = True
    if y1 != y2 or y2 != y3 :
        y_diff = True
    if z1 != z2 or z2 != z3 :
        z_diff = True

    if x_diff and y_diff :
        return True
    if x_diff and z_diff :
        return True
    if y_diff and z_diff :
        return True
    return False


class Router :

    ## @brief 初期化
    def __init__(self, graph, verbose) :
        self.__graph = graph
        self.__verbose = verbose

        dimension = graph.dimension
        self.__dimension = dimension
        self.__grid_num = dimension.grid_size
        self.__net_num = graph.net_num

        self.__cell_array = [Cell(index, dimension) for index in range(0, self.__grid_num)]

        w = dimension.width
        h = dimension.height
        d = dimension.depth
        for cell in self.__cell_array :
            x, y, z = cell.point.xyz
            if x > 0 :
                cell.set_adj_cell(0, self.__cell(Point(x - 1, y, z)))
            if x < w - 1 :
                cell.set_adj_cell(1, self.__cell(Point(x + 1, y, z)))
            if y > 0 :
                cell.set_adj_cell(2, self.__cell(Point(x, y - 1, z)))
            if y < h - 1 :
                cell.set_adj_cell(3, self.__cell(Point(x, y + 1, z)))
            if z > 0 :
                cell.set_adj_cell(4, self.__cell(Point(x, y, z - 1)))
            if z < d - 1 :
                cell.set_adj_cell(5, self.__cell(Point(x, y, z + 1)))

        self.__route_info_array = None

    ## @brief 経路情報をセットする．
    def set_routes(self, route_list) :
        self.__route_info_array = [RouteInfo(route_list[i]) for i in range(0, self.__net_num)]

    ## @brief 連結性を壊さずに線を引き直す．
    def reroute(self) :
        if self.__verbose :
            print('rerouting')

        t_length, t_bend = self.count()
        t_length0, t_bend0 = t_length, t_bend

        while True :
            if self.__verbose :
                print('  Total length = {:7d}'.format(t_length))
                print('  Total bends  = {:7d}'.format(t_bend))

            t_length0, t_bend0 = t_length, t_bend
            for i in range(0, self.__net_num) :
                self.__reroute(i)
            t_length, t_bend = self.count()
            if t_length >= t_length0 and t_bend >= t_bend0 :
                break

    ## @brief 配線結果を Solution に変換する．
    def to_solution(self) :
        solution = Solution()
        solution.set_size(self.__dimension)
        for net_id in range(0, self.__net_num) :
            route_info = self.__route_info_array[net_id]
            point = route_info._start_point
            solution.set_val(point, net_id + 1)
            for point in route_info._points :
                solution.set_val(point, net_id + 1)
            point = route_info._end_point
            solution.set_val(point, net_id + 1)
        return solution

    def count(self) :
        t_length = 0
        t_bend = 0
        for route_info in self.__route_info_array :
            t_length += len(route_info._points)
            t_bend += route_info.count_bends()
        return t_length, t_bend

    def __reroute(self, net_id) :
        # ラベルを初期化する．
        for cell in self.__cell_array :
            cell.__label = 0
        # net_id 以外の配線を障害物とみなす．
        for i in range(0, self.__net_num) :
            if i == net_id :
                continue
            route_info = self.__route_info_array[i]
            point = route_info._start_point
            self.__cell(point).__label = -1
            point = route_info._end_point
            self.__cell(point).__label = -1
            for point in route_info._points :
                self.__cell(point).__label = -1

        # net_id の配線経路を最短・最小曲がりで引き直す．
        route_info = self.__route_info_array[net_id]
        point = route_info._start_point
        start_cell = self.__cell(point)
        point = route_info._end_point
        end_cell = self.__cell(point)
        route_info._points = []
        self.__reroute_sub(start_cell, end_cell, route_info)

        # 作業用に作った Edge を解放する．
        for cell in self.__cell_array :
            for i in range(0, 6) :
                cell.set_backtrace_info(i, None)

    def __reroute_sub(self, start, end, route_info) :
        start.__label = 1
        queue = []
        queue.append(start)
        rpos = 0
        while True :
            assert rpos < len(queue)
            cell = queue[rpos]
            rpos += 1
            if cell == end :
                break
            for dir_id in range(0, 6) :
                cell1 = cell.adj_cell(dir_id)
                if cell1 == None :
                    continue
                if cell1.__label == 0 :
                    cell1.__label = cell.__label + 1
                    queue.append(cell1)

        # end から start までバックトレースを行う．
        mark = [False for i in range(0, self.__grid_num)]
        queue = []
        mark[end.index] = True
        queue.append(end)
        rpos = 0
        while True :
            assert rpos < len(queue)
            cell = queue[rpos]
            rpos += 1
            if cell == start :
                break
            label = cell.__label
            for dir_id in range(0, 6) :
                cell1 = cell.adj_cell(dir_id)
                if cell1 == None :
                    continue
                if cell1.__label != label - 1 :
                    continue
                if cell == end :
                    min_b = 0
                    min_edge = None
                else :
                    min_b = -1
                    min_edge = None
                    for dir_id in range(0, 6) :
                        edge = cell.backtrace_info(dir_id)
                        if edge == None :
                            continue
                        b = edge._bend_num
                        cell2 = edge._to
                        if check_bend(cell1.point, cell.point, cell2.point) :
                            b += 1
                        if min_b == -1 or min_b > b :
                            min_b = b
                            min_edge = edge
                edge = Edge(cell1, cell, min_b, min_edge)
                cell1.set_backtrace_info(dir_id ^ 1, edge)
                if not mark[cell1.index] :
                    mark[cell1.index] = True
                    queue.append(cell1)

        # 最短かつ最小曲がりの枝を見つける．
        min_edge = None
        min_b = -1
        for dir_id in range(0, 6) :
            edge = start.backtrace_info(dir_id)
            if edge == None :
                continue
            b = edge._bend_num
            if min_b == -1 or min_b > b :
                min_b = b
                min_edge = edge
        assert min_edge != None
        while True :
            cell = min_edge._to
            if cell == end :
                break
            route_info._points.append(cell.point)
            min_edge = min_edge._next

    def __cell(self, point) :
        index = self.__dimension.point_to_index(point)
        return self.__cell_array[index]
