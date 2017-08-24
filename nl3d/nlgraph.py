#! /usr/bin/env python3

## @file nlgraph.py
# @brief NlGraph の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlpoint import NlPoint
from nl3d.nlvia import NlVia
from nl3d.nlproblem import NlProblem


## @brief 節点を表すクラス
#
# 以下のメンバを持つ．
# - ID番号
# - 座標(_x, _y, _z)
# - 接続している枝のリスト(_edge_list)
# - 各方向の枝(_right_edge, _left_edge, _upper_edge, _lower_edge)
# - 終端の時に True となるフラグ(_is_terminal)
# - 終端の時の線分番号(_terminal_id)
# - ビアの時に True となるフラグ(_is_via)
# - ビアの時のビア番号(_via_id)
#
# ただし @property 属性のついたメンバ関数をメンバのようにアクセスすること．
class NlNode :

    ## @brief 初期化
    def __init__(self, id, x, y, z) :
        self._id = id
        self._x = x
        self._y = y
        self._z = z
        self._edge_list = []
        self._right_edge = None
        self._left_edge = None
        self._upper_edge = None
        self._lower_edge = None
        self._is_terminal = False
        self._terminal_id = None
        self._is_via = False
        self._via_id = None

    ## @brief 終端の印をつける．
    def set_terminal(self, net_id) :
        self._is_terminal = True
        self._terminal_id = net_id

    ## @brief ビアの印をつける．
    def set_via(self, via_id) :
        self._is_via = True
        self._via_id = via_id

    ## @brief 枝を追加する．
    # @param[in] edge 対象の枝
    # @param[in] dir 方向
    #
    # dir の意味は以下の通り
    # - 0: 右
    # - 1: 左
    # - 2: 上
    # - 3: 下
    def add_edge(self, edge, dir) :
        self._edge_list.append(edge)
        if dir == 0 :
            self._right_edge = edge
        elif dir == 1 :
            self._left_edge = edge
        elif dir == 2 :
            self._upper_edge = edge
        elif dir == 3 :
            self._lower_edge = edge


    ## @brief ID番号
    @property
    def id(self) :
        return self._id

    ## @brief X座標
    @property
    def x(self) :
        return self._x

    ## @brief Y座標
    @property
    def y(self) :
        return self._y

    ## @brief Z座標
    @property
    def z(self) :
        return self._z

    ## @brief 接続している枝のリストを返す
    @property
    def edge_list(self) :
        for edge in self._edge_list :
            assert edge._node1 == self or edge._node2 == self
        return self._edge_list

    ## @brief 右方向の枝を返す．
    #
    # なければ None を返す．
    @property
    def right_edge(self) :
        return self._right_edge

    ## @brief 左方向の枝を返す．
    #
    # なければ None を返す．
    @property
    def left_edge(self) :
        return self._left_edge

    ## @brief 上方向の枝を返す．
    #
    # なければ None を返す．
    @property
    def upper_edge(self) :
        return self._upper_edge

    ## @brief 下方向の枝を返す．
    #
    # なければ None を返す．
    @property
    def lower_edge(self) :
        return self._lower_edge

    ## @brief 終端フラグ
    @property
    def is_terminal(self) :
        return self._is_terminal

    ## @brief 終端番号
    #
    # is_terminal == False の場合の値は不定
    @property
    def terminal_id(self) :
        return self._terminal_id

    ## @brief ビアフラグ
    @property
    def is_via(self) :
        return self._is_via

    ## @brief ビア番号
    #
    # is_via == False の場合の値は不定
    @property
    def via_id(self) :
        return self._via_id


    ## @brief 終端かビアのとき True となるフラグ
    @property
    def is_block(self) :
        return self._is_terminal or self._is_via


    ## @brief 内容を表す文字列を返す．
    def str(self) :
        ans = '#{}: ({}, {}, {})'.format(self.id, self.x, self.y, self.z)

        if self.is_terminal :
            ans += ' [Net#{}]'.format(self.terminal_id)

        if self.is_via :
            ans += ' [Via#{}]'.format(self.via_id)

        return ans


## @brief 枝を表すクラス
#
# 以下のメンバを持つ．
# - ID番号
# - 両端の節点(_node1, _node2)
class NlEdge :

    ## @brief 初期化
    def __init__(self, id, node1, node2) :
        self._id = id
        self._node1 = node1
        self._node2 = node2

    ## @brief ID番号
    @property
    def id(self) :
        return self._id

    ## @brief ノード1
    @property
    def node1(self) :
        return self._node1

    ## @brief ノード2
    @property
    def node2(self) :
        return self._node2

    ## @brief 反対側のノードを返す．
    def alt_node(self, node) :
        if node == self._node1 :
            return self._node2
        elif node == self._node2 :
            return self._node1
        else :
            assert False


    ## @brief 内容を表す文字列を返す．
    def str(self) :
        return '#{}: ({}, {}, {}) - ({}, {}, {})'.format(self.id, \
                                                         self.node1.x, self.node1.y, self.node1.z,\
                                                         self.node2.x, self.node2.y, self.node2.z)


## @brief ナンバーリンクの問題を表すグラフ
class NlGraph :

    ## @brief 初期化
    # @param[in] problem 問題を表すオブジェクト(NlProblem)
    def __init__(self, problem) :
        self.set_problem(problem)


    ## @brief 問題を設定する．
    # @param[in] problem 問題を表すオブジェクト(NlProblem)
    def set_problem(self, problem) :
        self._width = problem.width
        self._height = problem.height
        self._depth = problem.depth

        self._net_num = problem.net_num
        self._via_num = problem.via_num

        # 節点を作る．
        # node_array[x][y][z] に (x, y, z) の節点が入る．
        # Python 特有の内包表記で one-liner で書けるけど1行が長すぎ．
        self._node_list = []
        self._node_array = [[[self._new_node(x, y, z)
                              for z in range(0, self._depth)] \
                             for y in range(0, self._height)] \
                            for x in range(0, self._width)]

        # 枝を作る．
        self._edge_list = []
        for z in range(0, self._depth) :
            # 水平の枝を作る．
            for x in range(0, self._width - 1) :
                for y in range(0, self._height) :
                    # (x, y) - (x + 1, y) を結ぶ枝
                    node1 = self._node_array[x][y][z]
                    node2 = self._node_array[x + 1][y][z]
                    self._new_edge(node1, node2, True)

            # 垂直の枝を作る．
            for x in range(0, self._width) :
                for y in range(0, self._height - 1) :
                    # (x, y) - (x, y + 1) を結ぶ枝
                    node1 = self._node_array[x][y][z]
                    node2 = self._node_array[x][y + 1][z]
                    self._new_edge(node1, node2, False)

        # 端子の印をつける．
        self._terminal_node_pair_list = []
        for net_id, (label, s, e) in enumerate(problem.net_list()) :
            node1 = self._node_array[s.x][s.y][s.z]
            node2 = self._node_array[e.x][e.y][e.z]
            node1.set_terminal(net_id)
            node2.set_terminal(net_id)
            self._terminal_node_pair_list.append((node1, node2))

        # ビアの印をつける．
        self._via_nodes_list = [[] for via_id in range(0, self._via_num)]
        for via_id, via in enumerate(problem.via_list()) :
            via_nodes = []
            for z in range(via.z1, via.z2 - via.z1 + 1) :
                node = self._node_array[via.x][via.y][z]
                node.set_via(via_id)
                via_nodes.append(node)
            self._via_nodes_list[via_id] = via_nodes

        # ビアを使うことのできるネットを求める．
        # 条件はネットの２つの終端の層番号をそのビアが含んでいること．
        # ただし2つの終端の層番号が等しいネットは除外する．
        # _via_net_list[via_id] に via_id と関係のある線分番号のリストが入る．
        # _net_via_list[net_id] に net_id と関係のあるビア番号のリストが入る．
        self._via_net_list = [[] for via_id in range(0, self._via_num)]
        self._net_via_list = [[] for net_id in range(0, self._net_num)]
        for via_id, via in enumerate(problem.via_list()) :
            z1 = via.z1
            z2 = via.z2
            net_list = []
            for net_id, (label, s, e) in enumerate(problem.net_list()) :
                if s.z != e.z and z1 <= s.z <= z2 and z1 <= e.z <= z2 :
                    net_list.append(net_id)
                    self._net_via_list[net_id].append(via_id)
            self._via_net_list[via_id] = net_list


    ## @brief 問題の幅
    @property
    def width(self) :
        return self._width


    ## @brief 問題の高さ
    @property
    def height(self) :
        return self._height


    ## @brief 問題の層数
    @property
    def depth(self) :
        return self._depth


    ## @brief ネット数
    @property
    def net_num(self) :
        return self._net_num


    ## @brief ビア数
    @property
    def via_num(self) :
        return self._via_num


    ## @brief ノードのリスト
    @property
    def node_list(self) :
        return self._node_list


    ## @brief 枝のリスト
    @property
    def edge_list(self) :
        return self._edge_list


    ## @brief 端点のノード対を返す．
    # @param[in] net_id 線分番号
    def terminal_node_pair(self, net_id) :
        return self._terminal_node_pair_list[net_id]


    ## @brief ネットに関係するビア番号のリストを返す．
    # @param[in] net_id 線分番号
    def net_via_list(self, net_id) :
        return self._net_via_list[net_id]


    ## @brief ビアのノードリストを返す．
    # @param[in] via_id ビア番号
    def via_node_list(self, via_id) :
        return self._via_nodes_list[via_id]


    ## @brief ビアに関係する線分番号のリストを返す．
    # @param[in] via_id ビア番号
    def via_net_list(self, via_id) :
        return self._via_net_list[via_id]


    ## @brief 座標を指定して対応するノードを返す．
    # @param[in] x, y, z 座標
    def node(self, x, y, z) :
        return self._node_array[x][y][z]


    ## @brief 枝を作る．
    # @param[in] node1, node2 両端の節点
    # @param[in] horizontal 水平方向の枝のとき True にする．
    def _new_edge(self, node1, node2, horizontal) :
        id = len(self._edge_list)
        edge = NlEdge(id, node1, node2)
        self._edge_list.append(edge)
        if horizontal :
            dir1 = 0
            dir2 = 1
        else :
            dir1 = 3
            dir2 = 4
        node1.add_edge(edge, dir1)
        node2.add_edge(edge, dir2)


    ## @brief ノードを作る．
    # @param[in] x, y, z 座標
    #
    # 結果を self._node_list に入れる．
    def _new_node(self, x, y, z) :
        id = len(self._node_list)
        node = NlNode(id, x, y, z)
        self._node_list.append(node)

        return node


    ## @brief 内容を出力する．
    def dump(self) :
        print('Nodes:')
        for node in self._node_list :
            print(node.str())

        print('')
        print('Edges:')
        for edge in self._edge_list :
            print(edge.str())
