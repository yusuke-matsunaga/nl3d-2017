#! /usr/bin/env python3

### @file v2016/graph.py
### @brief Graph の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

from nl3d.point import Point
from nl3d.via import Via
from nl3d.problem import Problem


### @brief 節点を表すクラス
###
### 以下のメンバを持つ．
### - ID番号
### - 位置(__point)
### - 接続している枝のリスト(__edge_list)
### - 各方向の枝(__x1_edge, __x2_edge, __y1_edge, __y2_edge)
### - 終端の時に True となるフラグ(__is_terminal)
### - 終端の時の線分番号(__terminal_id)
### - ビアの時に True となるフラグ(__is_via)
### - ビアの時のビア番号(__via_id)
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
        self.__is_via = False
        self.__via_id = None

    ### @brief 終端の印をつける．
    ### @param[in] net_id ネット番号
    def set_terminal(self, net_id) :
        self.__is_terminal = True
        self.__terminal_id = net_id

    ### @brief ビアの印をつける．
    ### @param[in] via_id ビア番号
    def set_via(self, via_id) :
        self.__is_via = True
        self.__via_id = via_id

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

    ### @brief ビアフラグ
    @property
    def is_via(self) :
        return self.__is_via

    ### @brief ビア番号
    ###
    ### is_via == False の場合の値は不定
    @property
    def via_id(self) :
        assert self.__is_via
        return self.__via_id

    ### @brief 終端かビアのとき True となるフラグ
    @property
    def is_block(self) :
        return self.__is_terminal or self.__is_via

    ### @brief 内容を表す文字列を返す．
    def str(self) :
        ans = '#{}: ({}, {}, {})'.format(self.id, self.x, self.y, self.z)

        if self.is_terminal :
            ans += ' [Net#{}]'.format(self.terminal_id)

        if self.is_via :
            ans += ' [Via#{}]'.format(self.via_id)

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
        self._via_num = problem.via_num

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
            # 水平の枝を作る．
            for x in range(0, self.width - 1) :
                for y in range(0, self.height) :
                    # (x, y) - (x + 1, y) を結ぶ枝
                    node1 = self.__node_array[x + 0][y][z]
                    node2 = self.__node_array[x + 1][y][z]
                    self.__new_edge(node1, node2, True)

            # 垂直の枝を作る．
            for x in range(0, self.width) :
                for y in range(0, self.height - 1) :
                    # (x, y) - (x, y + 1) を結ぶ枝
                    node1 = self.__node_array[x][y + 0][z]
                    node2 = self.__node_array[x][y + 1][z]
                    self.__new_edge(node1, node2, False)

        # 端子の印をつける．
        self.__terminal_node_pair_list = []
        for net_id, (label, s, e) in enumerate(problem.net_list()) :
            node1 = self.__node_array[s.x][s.y][s.z]
            node2 = self.__node_array[e.x][e.y][e.z]
            node1.set_terminal(net_id)
            node2.set_terminal(net_id)
            self.__terminal_node_pair_list.append((node1, node2))

        # ビアの印をつける．
        self.__via_nodes_list = [[] for via_id in range(0, self.via_num)]
        for via_id, via in enumerate(problem.via_list()) :
            via_nodes = []
            for z in range(via.z1, via.z2 - via.z1 + 1) :
                node = self.__node_array[via.x][via.y][z]
                node.set_via(via_id)
                via_nodes.append(node)
            self.__via_nodes_list[via_id] = via_nodes

        # ビアを使うことのできるネットを求める．
        # 条件はネットの２つの終端の層番号をそのビアが含んでいること．
        # ただし2つの終端の層番号が等しいネットは除外する．
        # __via_net_list[via_id] に via_id と関係のある線分番号のリストが入る．
        # __net_via_list[net_id] に net_id と関係のあるビア番号のリストが入る．
        self.__via_net_list = [[] for via_id in range(0, self.via_num)]
        self.__net_via_list = [[] for net_id in range(0, self.net_num)]
        for via_id, via in enumerate(problem.via_list()) :
            z1 = via.z1
            z2 = via.z2
            net_list = []
            for net_id, (label, s, e) in enumerate(problem.net_list()) :
                if s.z != e.z and z1 <= s.z <= z2 and z1 <= e.z <= z2 :
                    net_list.append(net_id)
                    self.__net_via_list[net_id].append(via_id)
            self.__via_net_list[via_id] = net_list

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

    ### @brief ビア数
    @property
    def via_num(self) :
        return self.__via_num

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

    ### @brief ネットに関係するビア番号のリストを返す．
    ### @param[in] net_id 線分番号
    def net_via_list(self, net_id) :
        return self.__net_via_list[net_id]

    ### @brief ビアのノードリストを返す．
    ### @param[in] via_id ビア番号
    def via_node_list(self, via_id) :
        return self.__via_nodes_list[via_id]

    ### @brief ビアに関係する線分番号のリストを返す．
    ### @param[in] via_id ビア番号
    def via_net_list(self, via_id) :
        return self.__via_net_list[via_id]

    ### @brief 座標を指定して対応するノードを返す．
    ### @param[in] x, y, z 座標
    def node(self, x, y, z) :
        return self.__node_array[x][y][z]

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
            dir1 = 2
            dir2 = 3
        node1.add_edge(edge, dir1)
        node2.add_edge(edge, dir2)

    ### @brief ノードを作る．
    ### @param[in] x, y, z 座標
    ###
    ### 結果を self._node_list に入れる．
    def __new_node(self, x, y, z) :
        id = len(self.__node_list)
        node = Node(id, x, y, z)
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
