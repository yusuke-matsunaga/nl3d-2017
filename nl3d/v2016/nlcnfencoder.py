#! /usr/bin/env python3

## @file nlcnfencoder.py
# @brief NlCnfEncoder の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

import math
from nl3d.nlgraph import NlNode, NlEdge, NlGraph
from nl3d.nlsolution import NlSolution
from nl3d.sat.satsolver import SatSolver
from nl3d.sat.satbool3 import SatBool3

## @brief 問題を表すCNF式を生成するクラス
#
# 内部に NlGraph の要素に対する変数の割り当て情報を持つ．
class NlCnfEncoder :

    ## @brief 初期化
    # @param[in] graph 問題を表すグラフ
    # @param[in] solver SATソルバ
    #
    # ここではSATの変数の割当のみ行う．
    def __init__(self, graph, solver) :
        self._graph = graph
        self._solver = solver
        nn = graph.net_num
        vn = graph.via_num

        # 枝に対応する変数を作る．
        # 結果は edge_var_list に格納する．
        # _edge_var_list[edge.id] に edge に対応する変数が入る．
        self._edge_var_list = [solver.new_variable() for edge in graph.edge_list]

        # 節点のラベルを表す変数のリストを作る．
        # 節点のラベルは log2(nn + 1) 個の変数で表す(binaryエンコーディング)
        # 結果は node_vars_list に格納する．
        # _node_vars_list[node.id] に node に対応する変数のリストが入る．
        nn_log2 = math.ceil(math.log2(nn + 1))
        self._node_vars_list = [[solver.new_variable() for i in range(0, nn_log2)] \
                                for node in graph.node_list]

        # ビアと線分の割り当てを表す変数を作る．
        # _nv_map[net_id][via_id] に net_id の線分を via_id のビアに接続する時 True となる変数を入れる．
        self._nv_map = [[solver.new_variable() \
                         for via_id in range(0, vn)] \
                        for net_id in range(0, nn)]


    ## @brief 基本的な制約を作る．
    # @param[in] no_slack すべてのマス目を使う制約を入れるとき True にするフラグ
    def make_base_constraint(self, no_slack) :
        # 各節点に対して隣接する枝の条件を作る．
        for node in self._graph.node_list :
            self._make_edge_constraint(node, no_slack)

        # 枝が選択された時にその両端のノードのラベルが等しくなるという制約を作る．
        for edge in self._graph.edge_list :
            self._make_adj_nodes_constraint(edge)

        # 各ビアについてただ1つの線分が割り当てられるという制約を作る．
        for via_id in range(0, self._graph.via_num) :
            self._make_via_net_constraint(via_id)

        # 各線分についてただ一つのビアが割り当てられるという制約を作る．
        #for net_id in range(0, self._graph.net_num) :
        #    self._make_net_via_constraint(net_id)




    ## @brief U字(コの字)制約を作る．
    #
    # node_00 -- edge1 -- node_10
    #    |                   |
    #    |                   |
    #  edge2               edge3
    #    |                   |
    #    |                   |
    # node_01 -- edge4 -- node_11
    #
    # edge1, edge2, edge3, edge4 の３つ以上が同時に使われる
    # 経路は存在しない．
    def make_ushape_constraint(self) :
        # 変数名は上の図に対応している．
        solver = self._solver
        for node_00 in self._graph.node_list :
            edge1 = node_00.right_edge
            edge2 = node_00.lower_edge
            if edge1 == None or edge2 == None :
                continue

            node_10 = edge1.alt_node(node_00)
            assert node_10 != None

            node_01 = edge2.alt_node(node_00)
            assert node_01 != None

            edge3 = node_10.lower_edge
            assert edge3 != None

            edge4 = node_01.right_edge
            assert edge4 != None

            node_11 = edge3.alt_node(node_10)
            assert node_11 != None

            var1 = self._edge_var(edge1)
            var2 = self._edge_var(edge2)
            var3 = self._edge_var(edge3)
            var4 = self._edge_var(edge4)


            if not (node_00.is_block or node_10.is_block) :
                solver.add_clause(-var1, -var2, -var3)
            if not (node_00.is_block or node_01.is_block) :
                solver.add_clause(-var1, -var2, -var4)
            if not (node_10.is_block or node_11.is_block) :
                solver.add_clause(-var1, -var3, -var4)
            if not (node_01.is_block or node_11.is_block) :
                solver.add_clause(-var2, -var3, -var4)


    ## @brief 2x3マスのコの字経路を禁止する制約を作る．
    #
    # node_00 -- edge_h1 -- node_10 -- edge_h2 -- node_20
    #    |                     |                     |
    #    |                     |                     |
    # edge_v1               edge_??               edge_v2
    #    |                     |                     |
    #    |                     |                     |
    # node_01 -- edge_h3 -- node_11 -- edge_h4 -- node_21
    #
    # 1: node_11 が終端かビアでない限り，edge_v1, edge_h1, edge_h2, edge_v2
    #    という経路は使えない．
    # 2: node_10 が終端化ビアでない限り，edge_v1, edge_h3, edge_h4, edge_v2
    #    という経路は使えない．
    #
    # これをタテ・ヨコの２方向に対して行う．
    def make_wshape_constraint(self) :
        solver = self._solver
        for node_00 in self._graph.node_list :
            # d は方向(0: ヨコ, 1: タテ)
            for d in range(0, 2) :
                edge_h1 = node_00.lower_edge if d else node_00.right_edge
                if edge_h1 == None :
                    continue
                node_10 = edge_h1.alt_node(node_00)
                if node_10.is_block :
                    continue

                edge_h2 = node_10.lower_edge if d else node_10.right_edge
                if edge_h2 == None :
                    continue
                node_20 = edge_h2.alt_node(node_10)

                edge_v1 = node_00.right_edge if d else node_00.lower_edge
                if edge_v1 == None :
                    continue
                edge_v2 = node_20.right_edge if d else node_20.lower_edge

                node_01 = edge_v1.alt_node(node_00)
                node_21 = edge_v2.alt_node(node_20)

                edge_h3 = node_01.lower_edge if d else node_01.right_edge
                node_11 = edge_h3.alt_node(node_01)
                if node_11.is_block :
                    continue

                edge_h4 = node_11.lower_edge if d else node_11.right_edge

                var1 = self._edge_var(edge_v1)
                var4 = self._edge_var(edge_v2)
                if not (node_00.is_block or node_20.is_block) :
                    var2 = self._edge_var(edge_h1)
                    var3 = self._edge_var(edge_h2)
                    solver.add_clause(-var1, -var2, -var3, -var4)
                if not (node_01.is_block or node_21.is_block) :
                    var2 = self._edge_var(edge_h3)
                    var3 = self._edge_var(edge_h4)
                    solver.add_clause(-var1, -var2, -var3, -var4)


    ## @brief 2x4マスのコの字経路を禁止する制約を作る．
    #
    # node_00 -- edge_h1 -- node_10 -- edge_h2 -- node_20 -- edge_h3 -- node_30
    #    |                     |                     |                     |
    #    |                     |                     |                     |
    # edge_v1               edge_??               edge_??               edge_v2
    #    |                     |                     |                     |
    #    |                     |                     |                     |
    # node_01 -- edge_h4 -- node_11 -- edge_h5 -- node_21 -- edge_h6 -- node_31
    #
    # 1: node_11, node_21 が終端かビアでない限り，
    #    edge_v1, edge_h1, edge_h2, edge_h3, edge_v2 という経路は使えない．
    # 2: node_10, node_20 が終端かビアでない限り，
    #    edge_v1, edge_h4, edge_h5, edge_h6, edge_v2 という経路は使えない．
    #
    # これをタテ・ヨコの２方向に対して行う．
    def make_w2shape_constraint(self) :
        solver = self._solver
        for node_00 in self._graph.node_list :
            # d は方向(0: ヨコ, 1: タテ)
            for d in range(0, 2) :
                edge_h1 = node_00.lower_edge if d else node_00.right_edge
                if edge_h1 == None :
                    continue
                node_10 = edge_h1.alt_node(node_00)
                if node_10.is_block :
                    continue

                edge_h2 = node_10.lower_edge if d else node_10.right_edge
                if edge_h2 == None :
                    continue
                node_20 = edge_h2.alt_node(node_10)
                if node_20.is_block :
                    continue

                edge_h3 = node_20.lower_edge if d else node_20.right_edge
                if edge_h3 == None :
                    continue
                node_30 = edge_h3.alt_node(node_20)

                edge_v1 = node_00.right_edge if d else node_00.lower_edge
                if edge_v1 == None :
                    continue
                node_01 = edge_v1.alt_node(node_00)

                edge_v2 = node_30.right_edge if d else node_30.lower_edge

                edge_h4 = node_01.lower_edge if d else node_01.right_edge
                node_11 = edge_h4.alt_node(node_01)
                if node_11.is_block :
                    continue

                edge_h5 = node_11.lower_edge if d else node_11.right_edge
                node_21 = edge_h5.alt_node(node_11)
                if node_21.is_block :
                    continue

                edge_h6 = node_21.lower_edge if d else node_21.right_edge

                node_31 = edge_h6.alt_node(node_21)

                var_v1 = self._edge_var(edge_v1)
                var_v2 = self._edge_var(edge_v2)
                if not (node_00.is_block or node_30.is_block) :
                    var_h1 = self._edge_var(edge_h1)
                    var_h2 = self._edge_var(edge_h2)
                    var_h3 = self._edge_var(edge_h3)
                    solver.add_clause(-var_v1, -var_v2, -var_h1, -var_h2, -var_h3)
                if not (node_01.is_block or node_31.is_block) :
                    var_h4 = self._edge_var(edge_h4)
                    var_h5 = self._edge_var(edge_h5)
                    var_h6 = self._edge_var(edge_h6)
                    solver.add_clause(-var_v1, -var_v2, -var_h4, -var_h5, -var_h6)


    ## @brief SATモデルから解(NlSolution)を作る．
    def model_to_solution(self, model) :
        solution = NlSolution()
        solution.set_size(self._graph.width, self._graph.height, self._graph.depth)
        for net_id in range(0, self._graph.net_num) :
            start, end = self._graph.terminal_node_pair(net_id)
            prev = None
            node = start
            while node != end :
                solution.set_val(node.x, node.y, node.z, net_id + 1)
                next = None
                for edge in node.edge_list :
                    if model[self._edge_var(edge)] != SatBool3.B3True :
                        continue
                    node1 = edge.alt_node(node)
                    if node1 == prev :
                        continue
                    next = node1
                if next == None :
                    # このノードがビアなら end の層まで移動する．
                    assert node.is_via
                    assert start.z != end.z
                    if start.z < end.z :
                        for i in range(start.z, end.z) :
                            solution.set_val(node.x, node.y, i + 1, net_id + 1)
                    else :
                        for i in range(start.z, end.z, -1) :
                            solution.set_val(node.x, node.y, i - 1, net_id + 1)
                    next = self._graph.node(node.x, node.y, end.z)
                assert next != None
                prev = node
                node = next
            solution.set_val(node.x, node.y, node.z, net_id + 1)

        return solution


    ## @brief ノードに接続する枝に関する制約を作る．
    # @param[in] no_slack すべてのマス目を使う制約を入れるときに True にするフラグ
    #
    # 具体的には
    # - 終端の場合
    #   ただ一つの枝のみが選ばれる．
    # - ビアの場合
    #   nv_map の変数によって終端になる場合と孤立する場合がある．
    # - それ以外
    #   全て選ばれないか2つの枝が選ばれる．
    def _make_edge_constraint(self, node, no_slack) :
        # node に接続している枝の変数のリスト
        evar_list = [self._edge_var_list[edge.id] for edge in node.edge_list]

        if node.is_terminal :
            # node が終端の場合

            # ただ一つの枝が選ばれる．
            self._make_one_hot(evar_list)

            # 同時にラベルの変数を固定する．
            self._make_label_constraint(node, node.terminal_id)

        elif node.is_via :
            # node がビアの場合
            # この層に終端を持つ線分と結びついている時はただ一つの枝が選ばれる．
            via_id = node.via_id
            for net_id in self._graph.via_net_list(via_id) :
                cvar = self._nv_map[net_id][via_id]
                node1, node2 = self._graph.terminal_node_pair(net_id)
                if node1.z != node.z and node2.z != node.z :
                    # このビアは net_id の線分には使えない．
                    # このノードに接続する枝は選ばれない．
                    self._make_conditional_zero_hot(cvar, evar_list)
                else :
                    # このビアを終端と同様に扱う．
                    self._make_conditional_one_hot(cvar, evar_list)

                    # ラベルの制約を追加する．
                    self._make_conditional_label_constraint(cvar, node, net_id)
        else :
            if no_slack :
                # 常に２個の枝が選ばれる．
                self._make_two_hot(evar_list)
            else :
                # ０個か２個の枝が選ばれる．
                self._make_zero_or_two_hot(evar_list)


    ## @brief via_id に関してただ一つの線分が選ばれるという制約を作る．
    def _make_via_net_constraint(self, via_id) :
        # このビアに関係するネットを調べ，対応するビア割り当て変数のリストを作る．
        vars_list = [self._nv_map[net_id][via_id] for net_id in self._graph.via_net_list(via_id)]

        # この変数に対する one-hot 制約を作る．
        self._make_one_hot(vars_list)


    ## @brief net_id に関してただ一つのビアが選ばれるという制約を作る．
    def _make_net_via_constraint(self, net_id) :
        # このネットに関係のあるビアを調べ，対応するビア割り当て変数のリストを作る．
        vars_list = [self._nv_map[net_id][via_id] for via_id in self._graph.net_via_list(net_id)]

        # この変数に対する one-hot 制約を作る．
        self._make_one_hot(vars_list)


    ## @brief 枝の両端のノードのラベルに関する制約を作る．
    # @param[in] edge 対象の枝
    #
    # 具体的にはその枝が選ばれているとき両端のノードのラベルは等しい
    def _make_adj_nodes_constraint(self, edge) :
        evar = self._edge_var_list[edge.id]
        nvar_list1 = self._node_vars_list[edge.node1.id]
        nvar_list2 = self._node_vars_list[edge.node2.id]
        n = len(nvar_list1)
        for i in range(0, n) :
            nvar1 = nvar_list1[i]
            nvar2 = nvar_list2[i]
            self._make_conditional_equal(evar, nvar1, nvar2)


    ## @brief ラベル値を固定する制約を作る．
    # @param[in] node 対象のノード
    # @param[in] net_id 固定する線分番号
    def _make_label_constraint(self, node, net_id) :
        lvar_list = self._node_vars_list[node.id]
        for i, lvar in enumerate(lvar_list) :
            if (1 << i) & (net_id + 1) :
                self._solver.add_clause(lvar)
            else :
                self._solver.add_clause(-lvar)


    ## @brief 条件付きでラベル値を固定する制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] node 対象のノード
    # @param[in] net_id 固定する線分番号
    def _make_conditional_label_constraint(self, cvar, node, net_id) :
        lvar_list = self._node_vars_list[node.id]
        for i, lvar in enumerate(lvar_list) :
            if (1 << i) & (net_id + 1) :
                self._solver.add_clause(-cvar, lvar)
            else :
                self._solver.add_clause(-cvar, -lvar)


    ## @brief 枝に対する変数番号を返す．
    # @param[in] edge 対象の枝
    def _edge_var(self, edge) :
        return self._edge_var_list[edge.id]


    ## @brief 条件付きでリストの中の変数がすべて False となる制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] var_list 対象の変数のリスト
    def _make_conditional_zero_hot(self, cvar, var_list) :
        solver = self._solver
        for var in var_list :
            solver.add_clause(-cvar, -var)


    ## @brief リストの中の変数が1つだけ True となる制約を作る．
    # @param[in] var_list 対象の変数のリスト
    def _make_one_hot(self, var_list) :
        n = len(var_list)
        solver = self._solver
        # 要素数で場合分け
        if n == 2 :
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause(-var0, -var1)
            solver.add_clause( var0,  var1)
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause(-var0, -var1       )
            solver.add_clause(-var0,        -var2)
            solver.add_clause(       -var1, -var2)
            solver.add_clause( var0,  var1,  var2)
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause(-var0, -var1              )
            solver.add_clause(-var0,        -var2       )
            solver.add_clause(-var0,               -var3)
            solver.add_clause(       -var1, -var2       )
            solver.add_clause(       -var1,        -var3)
            solver.add_clause(              -var2, -var3)
            solver.add_clause( var0,  var1,  var2,  var3)
        else :
            # 一般形
            for i in range(0, n - 1) :
                var0 = var_list[i]
                for j in range(i + 1, n) :
                    var1 = var_list[j]
                    solver.add_clause(-var0, -var1)
            solver.add_clause(var_list)


    ## @brief 条件付きでリストの中の変数が1つだけ True となる制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] var_list 対象の変数のリスト
    def _make_conditional_one_hot(self, cvar, var_list) :
        solver = self._solver
        n = len(var_list)
        # 要素数で場合分け
        if n == 2 :
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause(-cvar, -var0, -var1)
            solver.add_clause(-cvar,  var0,  var1)
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause(-cvar, -var0, -var1       )
            solver.add_clause(-cvar, -var0,        -var2)
            solver.add_clause(-cvar,        -var1, -var2)
            solver.add_clause(-cvar,  var0,  var1,  var2)
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause(-cvar, -var0, -var1              )
            solver.add_clause(-cvar, -var0,        -var2       )
            solver.add_clause(-cvar, -var0,               -var3)
            solver.add_clause(-cvar,        -var1, -var2       )
            solver.add_clause(-cvar,        -var1,        -var3)
            solver.add_clause(-cvar,               -var2, -var3)
            solver.add_clause(-cvar,  var0,  var1,  var2,  var3)
        else :
            assert False


    ## @brief リストの中の変数が2個 True になるという制約
    # @param[in] var_list 対象の変数のリスト
    def _make_two_hot(self, var_list) :
        solver = self._solver
        n = len(var_list)
        # 要素数で場合分け
        if n == 2 :
            # いつも選ばれる．
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause(var0)
            solver.add_clause(var1)
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause(-var0, -var1, -var2)
            solver.add_clause( var0,  var1       )
            solver.add_clause( var0,         var2)
            solver.add_clause(        var1,  var2)
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause(-var0, -var1, -var2       )
            solver.add_clause(-var0, -var1,        -var3)
            solver.add_clause(-var0,        -var2, -var3)
            solver.add_clause(       -var1, -var2, -var3)
            solver.add_clause( var0,  var1,  var2       )
            solver.add_clause( var0,  var1,         var3)
            solver.add_clause( var0,         var2,  var3)
            solver.add_clause(        var1,  var2,  var3)
        else :
            assert False


    ## @brief リストの中の変数が0個か2個 True になるという制約
    # @param[in] var_list 対象の変数のリスト
    def _make_zero_or_two_hot(self, var_list) :
        solver = self._solver
        n = len(var_list)
        # 要素数で場合分け
        if n == 2 :
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause( var0, -var1)
            solver.add_clause(-var0,  var1)
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause(-var0, -var1, -var2)
            solver.add_clause( var0,  var1, -var2)
            solver.add_clause( var0, -var1,  var2)
            solver.add_clause(-var0,  var1,  var2)
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause(-var0, -var1, -var2       )
            solver.add_clause(-var0, -var1,        -var3)
            solver.add_clause(-var0,        -var2, -var3)
            solver.add_clause(       -var1, -var2, -var3)
            solver.add_clause( var0,  var1,  var2, -var3)
            solver.add_clause( var0,  var1, -var2,  var3)
            solver.add_clause( var0, -var1,  var2,  var3)
            solver.add_clause(-var0,  var1,  var2,  var3)
        else :
            assert False


    ## @brief 条件付きで２つの変数が等しくなるという制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] var1, var2 対象の変数
    def _make_conditional_equal(self, cvar, var1, var2) :
        solver = self._solver
        solver.add_clause(-cvar, -var1,  var2)
        solver.add_clause(-cvar,  var1, -var2)

# end-of-class NlCnfEncoder
