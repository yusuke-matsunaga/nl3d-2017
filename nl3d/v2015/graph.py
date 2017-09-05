#! /usr/bin/env python3

### @file v2015/graph.py
### @brief Graph の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

from nl3d.point import Point
from nl3d.problem import Problem


### @brief 節点を表すクラス
###
### 以下のメンバを持つ．
### - ID番号
### - 位置(__point)
### - 接続してeいる枝のリスト(__edge_list)
### - 各方向の枝(__x1_edge, __x2_edge, __y1_edge, __y2_edge)
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
        else :
            assert False

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
    def edge(self, dir_id) :
        if dir_id == 0 :
            return self.__x1_edge
        elif dir_id == 1 :
            return self.__x2_edge
        elif dir_id == 2 :
            return self.__y1_edge
        elif dir_id == 3 :
            return self.__y2_edge
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

    ### @brief 隣接するノードを返す．
    ### @param[in] dir_id 方向
    ###
    ### dir_idの意味は以下の通り
    ### - 0: 右(x1)
    ### - 1: 左(x2)
    ### - 2: 上(y1)
    ### - 3: 下(y2)
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
        assert self.__is_terminal
        return self.__terminal_id

    ### @brief 内容を表す文字列を返す．
    def str(self) :
        ans = '#{}: ({}, {}, {})'.format(self.id, self.x, self.y, self.z)

        if self.is_terminal :
            ans += ' [Net#{}]'.format(self.terminal_id)

        return ans


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


### @brief ナンバーリンクの問題を表すグラフ(ADC2016バージョン)
class Graph :

    ### @brief 初期化
    ### @param[in] problem 問題を表すオブジェクト(Problem)
    def __init__(self, problem) :
        self.set_problem(problem)

    ### @brief 問題を設定する．
    ### @param[in] problem 問題を表すオブジェクト(Problem)
    def set_problem(self, problem) :
        self.__dim = problem.dimension
        self._net_num = problem.net_num

        # 節点を作る．
        # node_array[x][y] に (x, y) の節点が入る．
        # Python 特有の内包表記で one-liner で書けるけど1行が長すぎ．
        self.__node_list = []
        self.__node_array = [[self.__new_node(x, y)
                              for y in range(0, self.height)] \
                             for x in range(0, self.width)]

        # 枝を作る．
        self.__edge_list = []
        # 水平の枝を作る．
        for x in range(0, self.width - 1) :
            for y in range(0, self.height) :
                # (x, y) - (x + 1, y) を結ぶ枝
                node1 = self.__node_array[x + 0][y]
                node2 = self.__node_array[x + 1][y]
                self.__new_edge(node1, node2, True)

        # 垂直の枝を作る．
        for x in range(0, self.width) :
            for y in range(0, self.height - 1) :
                # (x, y) - (x, y + 1) を結ぶ枝
                node1 = self.__node_array[x][y + 0]
                node2 = self.__node_array[x][y + 1]
                self.__new_edge(node1, node2, False)

        # 端子の印をつける．
        self.__terminal_node_pair_list = []
        for net_id, (label, s, e) in enumerate(problem.net_list()) :
            node1 = self.__node_array[s.x][s.y]
            node2 = self.__node_array[e.x][e.y]
            node1.set_terminal(net_id)
            node2.set_terminal(net_id)
            self.__terminal_node_pair_list.append((node1, node2))


    ### @brief 問題の幅
    @property
    def width(self) :
        return self.__dim.width

    ### @brief 問題の高さ
    @property
    def height(self) :
        return self.__dim.height

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
    ### @param[in] x, y 座標
    def node(self, x, y) :
        return self.__node_array[x][y]

    ### @brief 枝を作る．
    ### @param[in] node1, node2 両端の節点
    ### @param[in] horizontal 水平方向の枝のとき True にする．
    def __new_edge(self, node1, node2, horizontal) :
        id = len(self.__edge_list)
        edge = Edge(id, node1, node2)
        self.__edge_list.append(edge)
        if horizontal :
            dir1 = 0
            dir2 = 1
        else :
            dir1 = 3
            dir2 = 4
        node1.add_edge(edge, dir1)
        node2.add_edge(edge, dir2)

    ### @brief ノードを作る．
    ### @param[in] x, y 座標
    ###
    ### 結果を self._node_list に入れる．
    def __new_node(self, x, y) :
        id = len(self.__node_list)
        node = Node(id, Point(x, y, 0))
        self.__node_list.append(node)

        return node

    ### @brief 内容を出力する．
    def dump(self) :
        print('Nodes:')
        for node in self.__node_list :
            print(node.str())

        print('')
        print('Edges:')
        for edge in self.__edge_list :
            print(edge.str())

# end of graph.py
