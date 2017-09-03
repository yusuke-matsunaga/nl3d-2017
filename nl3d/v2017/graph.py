#! /usr/bin/env python3

### @file graph.py
### @brief Graph の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

from nl3d.v2017.point import Point
from nl3d.v2017.problem import Problem


### @brief 節点を表すクラス
###
### 以下のメンバを持つ．
### - インデックス番号
### - 位置(__point)
### - 接続している枝のリスト(__edge_list)
### - 各方向の枝(__x1_edge, __x2_edge, __y1_edge, __y2_edge, __z1__edge, __z2_edge)
### - 終端の時に True となるフラグ(__is_terminal)
### - 終端の時の線分番号(__terminal_id)
###
### ただし @property 属性のついたメンバ関数をメンバのようにアクセスすること．
class Node :

    ### @brief 初期化
    ### @param[in] id ID番号
    ### @param[in] point 位置
    def __init__(self, id, point) :
        self.__id = id
        self.__point = point
        self.__edge_list = []
        self.__x1_edge = None
        self.__x2_edge = None
        self.__y1_edge = None
        self.__y2_edge = None
        self.__z1_edge = None
        self.__z2_edge = None
        self.__is_terminal = False
        self.__terminal_id = None

    ### @brief 終端の印をつける．
    ### @param[in] net_id ネット番号
    def set_terminal(self, net_id) :
        self.__is_terminal = True
        self.__terminal_id = net_id

    ### @brief 枝を追加する．
    ### @param[in] edge 対象の枝
    ### @param[in] dir_id 方向
    ###
    ### dir_id の意味は以下の通り
    ### - 0: 右(x1)
    ### - 1: 左(x2)
    ### - 2: 上(y1)
    ### - 3: 下(y2)
    ### - 4:   (z1)
    ### - 5:   (z2)
    def add_edge(self, edge, dir_id) :
        self.__edge_list.append(edge)
        if dir_id == 0 :
            self.__x1_edge = edge
        elif dir_id == 1 :
            self.__x2_edge = edge
        elif dir_id == 2 :
            self.__y1_edge = edge
        elif dir_id == 3 :
            self.__y2_edge = edge
        elif dir_id == 4 :
            self.__z1_edge = edge
        elif dir_id == 5 :
            self.__z2_edge = edge

    ### @brief ID番号
    @property
    def id(self) :
        return self.__id

    ### @brief 位置(point)
    @property
    def point(self) :
        return self.__point

    ### @brief X座標
    @property
    def x(self) :
        return self.__point.x

    ### @brief Y座標
    @property
    def y(self) :
        return self.__point.y

    ### @brief Z座標
    @property
    def z(self) :
        return self.__point.z

    ### @brief 接続している枝のリストのジェネレータを返す
    @property
    def edge_list(self) :
        for edge in self.__edge_list :
            # sanity check
            assert edge.node1 == self or edge.node2 == self
            yield edge

    ### @brief dir_id で指定された枝を返す．
    ###
    ### dir_idの意味は以下の通り
    ### - 0: 右(x1)
    ### - 1: 左(x2)
    ### - 2: 上(y1)
    ### - 3: 下(y2)
    ### - 4:   (z1)
    ### - 5:   (z2)
    def edge(self, dir_id) :
        if dir_id == 0 :
            return self.__x1_edge
        elif dir_id == 1 :
            return self.__x2_edge
        elif dir_id == 2 :
            return self.__y1_edge
        elif dir_id == 3 :
            return self.__y2_edge
        elif dir_id == 4 :
            return self.__z1_edge
        elif dir_id == 5 :
            return self.__z2_edge
        else :
            assert False

    ### @brief x1方向の枝
    ###
    ### なければ None を返す．
    @property
    def x1_edge(self) :
        return self.__x1_edge

    ### @brief x2の枝
    ###
    ### なければ None を返す．
    @property
    def x2_edge(self) :
        return self.__x2_edge

    ### @brief y1方向の枝
    ###
    ### なければ None を返す．
    @property
    def y1_edge(self) :
        return self.__y1_edge

    ### @brief y2方向の枝
    ###
    ### なければ None を返す．
    @property
    def y2_edge(self) :
        return self.__y2_edge

    ### @brief z1方向の枝
    ###
    ### なければ None を返す．
    @property
    def z1_edge(self) :
        return self.__z1_edge

    ### @brief z2方向の枝
    ###
    ### なければ None を返す．
    @property
    def z2_edge(self) :
        return self.__z2_edge

    ### @brief 隣接するノードを返す．
    ### @param[in] dir_id 方向
    ###
    ### dir_idの意味は以下の通り
    ### - 0: 右(x1)
    ### - 1: 左(x2)
    ### - 2: 上(y1)
    ### - 3: 下(y2)
    ### - 4:   (z1)
    ### - 5:   (z2)
    def adj_node(self, dir_id) :
        edge = self.edge(dir_id)
        if edge == None :
            return None
        return edge.alt_node(self)

    ### @brief 終端フラグ
    @property
    def is_terminal(self) :
        return self.__is_terminal

    ### @brief 終端番号
    ###
    ### is_terminal == False の場合の値は不定
    @property
    def terminal_id(self) :
        return self.__terminal_id

    ### @brief 内容を表す文字列を返す．
    def str(self) :
        ans = '#{:04d}: {}'.format(self.id, self.point)

        if self.is_terminal :
            ans += ' [Net#{}]'.format(self.terminal_id)

        return ans

    ### @brief デバッグ用の出力
    def dump(self) :
        print(self.str(), end='')
        if self.x1_edge :
            print(' x1: #{:04d}'.format(self.x1_edge.id), end='')
        if self.x2_edge :
            print(' x2: #{:04d}'.format(self.x2_edge.id), end='')
        if self.y1_edge :
            print(' y1: #{:04d}'.format(self.y1_edge.id), end='')
        if self.y2_edge :
            print(' y2: #{:04d}'.format(self.y2_edge.id), end='')
        if self.z1_edge :
            print(' z1: #{:04d}'.format(self.z1_edge.id), end='')
        if self.z2_edge :
            print(' z2: #{:04d}'.format(self.z2_edge.id), end='')
        print('')


### @brief 枝を表すクラス
###
### 以下のメンバを持つ．
### - ID番号
### - 両端の節点(__node1, __node2)
class Edge :

    ### @brief 初期化
    ### @param[in] id ID番号
    ### @param[in] node1, node2 接続しているノード
    def __init__(self, id, node1, node2) :
        self.__id = id
        self.__node1 = node1
        self.__node2 = node2

    ### @brief ID番号
    @property
    def id(self) :
        return self.__id

    ### @brief ノード1
    @property
    def node1(self) :
        return self.__node1

    ### @brief ノード2
    @property
    def node2(self) :
        return self.__node2

    ### @brief 反対側のノードを返す．
    ### @param[in] node 自分のノード
    def alt_node(self, node) :
        if node == self.__node1 :
            return self.__node2
        elif node == self.__node2 :
            return self.__node1
        else :
            assert False

    ### @brief 内容を表す文字列を返す．
    def str(self) :
        return '#{}: {} - {}'.format(self.id, self.node1.str(), self.node2.str())

    ### @brief デバッグ用の出力
    def dump(self) :
        print(self.str())


### @brief ナンバーリンクの問題を表すグラフ
class Graph :

    ### @brief 初期化
    ### @param[in] problem 問題を表すオブジェクト(Problem)
    def __init__(self, problem) :
        self.set_problem(problem)


    ### @brief 問題を設定する．
    ### @param[in] problem 問題を表すオブジェクト(Problem)
    def set_problem(self, problem) :
        self.__dim = problem.dimension
        self.__net_num = problem.net_num

        # 節点を作る．
        # node_array[x][y][z] に (x, y, z) の節点が入る．
        # Python 特有の内包表記で one-liner で書けるけど1行が長すぎ．
        self.__node_list = []
        self.__node_array = [[[self.__new_node(x, y, z)
                               for z in range(0, self.depth)] \
                              for y in range(0, self.height)] \
                             for x in range(0, self.width)]

        # 枝を作る．
        self.__edge_list = []
        for z in range(0, self.depth) :
            # x方向の枝を作る．
            for x in range(0, self.width - 1) :
                for y in range(0, self.height) :
                    # (x, y, z) - (x + 1, y, z) を結ぶ枝
                    node1 = self.__node_array[x    ][y][z]
                    node2 = self.__node_array[x + 1][y][z]
                    self.__new_edge(node1, node2, 0)

            # y方向の枝を作る．
            for x in range(0, self.width) :
                for y in range(0, self.height - 1) :
                    # (x, y, z) - (x, y + 1, z) を結ぶ枝
                    node1 = self.__node_array[x][y    ][z]
                    node2 = self.__node_array[x][y + 1][z]
                    self.__new_edge(node1, node2, 1)

        # z 方向の枝を作る．
        for x in range(0, self.width) :
            for y in range(0, self.height) :
                for z in range(0, self.depth - 1) :
                    # (x, y, z) - (x, y, z + 1) を結ぶ枝
                    node1 = self.__node_array[x][y][z    ]
                    node2 = self.__node_array[x][y][z + 1]
                    self.__new_edge(node1, node2, 2)

        # 端子の印をつける．
        self.__terminal_node_pair_list = []
        for net_id, (label, s, e) in enumerate(problem.net_list()) :
            node1 = self.__node_array[s.x][s.y][s.z]
            node2 = self.__node_array[e.x][e.y][e.z]
            node1.set_terminal(net_id)
            node2.set_terminal(net_id)
            self.__terminal_node_pair_list.append((node1, node2))

    ### @brief 問題のサイズ
    @property
    def dimension(self) :
        return self.__dim

    ### @brief 問題の幅
    @property
    def width(self) :
        return self.__dim.width

    ### @brief 問題の高さ
    @property
    def height(self) :
        return self.__dim.height

    ### @brief 問題の層数
    @property
    def depth(self) :
        return self.__dim.depth

    ### @brief ネット数
    @property
    def net_num(self) :
        return self.__net_num

    ### @brief ノードのリスト
    @property
    def node_list(self) :
        return self.__node_list

    ### @brief 枝のリスト
    @property
    def edge_list(self) :
        return self.__edge_list

    ### @brief 端点のノード対を返す．
    ### @param[in] net_id 線分番号
    def terminal_node_pair(self, net_id) :
        return self.__terminal_node_pair_list[net_id]

    ### @brief 座標を指定して対応するノードを返す．
    ### @param[in] x, y, z 座標
    def node(self, x, y, z) :
        return self.__node_array[x][y][z]

    ### @brief 位置(Point) から対応するノードを返す．
    ### @param[in] point 位置(Point)
    def node_from_point(self, point) :
        x, y, z = point.xyz
        return self.node(x, y, z)

    ### @brief 枝を作る．
    ### @param[in] node1, node2 両端の節点
    ### @param[in] dir_base 方向を表す数字
    ###
    ### dir_base の意味は以下の通り
    ### - 0: x 方向
    ### - 1: y 方向
    ### - 2: z 方向
    def __new_edge(self, node1, node2, dir_base) :
        id = len(self.__edge_list)
        edge = Edge(id, node1, node2)
        self.__edge_list.append(edge)
        dir1 = dir_base * 2 + 0
        dir2 = dir_base * 2 + 1
        node1.add_edge(edge, dir2)
        node2.add_edge(edge, dir1)

    ### @brief ノードを作る．
    ### @param[in] x, y, z 座標
    ###
    ### 結果を self._node_list に入れる．
    def __new_node(self, x, y, z) :
        id = len(self.__node_list)
        node = Node(id, Point(x, y, z))
        self.__node_list.append(node)

        return node


    ### @brief 内容を出力する．
    def dump(self) :
        print('Nodes:')
        for node in self.__node_list :
            node.dump()

        print('')
        print('Edges:')
        for edge in self.__edge_list :
            edge.dump()
