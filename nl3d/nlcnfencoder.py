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
from pym_sat import Solver, VarId, Literal, Bool3


## @brief 問題を表すCNF式を生成するクラス
#
# 内部に NlGraph の要素に対する変数の割り当て情報を持つ．
class NlCnfEncoder :

    ## @brief 初期化
    # @param[in] graph 問題を表すグラフ
    # @param[in] solver SATソルバの型を表す文字列
    #
    # ここではSATの変数の割当のみ行う．
    def __init__(self, graph, solver_type) :
        solver = Solver(solver_type)
        self.__graph = graph
        self.__solver = solver

        # 枝に対応する変数を作る．
        # 結果は edge_var_list に格納する．
        # __edge_var_list[edge.id] に edge に対応する変数が入る．
        # 実際にはその変数に対応するリテラルを入れる．
        self.__edge_var_list = [Literal(solver.new_variable()) for edge in graph.edge_list]

        # 節点のラベルを表す変数のリストを作る．
        # 節点のラベルは log2(nn + 1) 個の変数で表す(binaryエンコーディング)
        # 結果は __node_vars_list に格納する．
        # __node_vars_list[node.id] に node に対応する変数のリストが入る．
        # 実際にはその変数に対応するリテラルを入れる．
        nn = graph.net_num
        nn_log2 = math.ceil(math.log2(nn + 1))
        self.__node_vars_list = [[Literal(solver.new_variable()) for i in range(0, nn_log2)] \
                                 for node in graph.node_list]

    ## @brief 基本的な制約を作る．
    # @param[in] no_slack すべてのマス目を使う制約を入れるとき True にするフラグ
    def make_base_constraint(self, no_slack) :
        graph = self.__graph
        # 各節点に対して隣接する枝の条件を作る．
        for node in graph.node_list :
            self.__make_edge_constraint(node, no_slack)

        # 枝が選択された時にその両端のノードのラベルが等しくなるという制約を作る．
        for edge in graph.edge_list :
            self.__make_adj_nodes_constraint(edge)


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
    #
    # これを3方向で行う．
    def make_ushape_constraint(self) :
        graph = self.__graph
        # 変数名は上の図に対応している．
        for node in graph.node_list :
            self.__ushape_sub(node, 1, 3)
            self.__ushape_sub(node, 1, 5)
            self.__ushape_sub(node, 3, 5)

    ## @brief make_ushape_constraint() の下請け関数
    def __ushape_sub(self, node_00, dir1, dir2) :
        edge1 = node_00.edge(dir1)
        edge2 = node_00.edge(dir2)
        if edge1 == None or edge2 == None :
            return

        node_10 = edge1.alt_node(node_00)
        assert node_10 != None

        node_01 = edge2.alt_node(node_00)
        assert node_01 != None

        edge3 = node_10.edge(dir2)
        assert edge3 != None

        edge4 = node_01.edge(dir1)
        assert edge4 != None

        node_11 = edge3.alt_node(node_10)
        assert node_11 != None

        solver = self.__solver
        var1 = self.__edge_var(edge1)
        var2 = self.__edge_var(edge2)
        var3 = self.__edge_var(edge3)
        var4 = self.__edge_var(edge4)
        if not (node_00.is_terminal or node_10.is_terminal) :
            solver.add_clause([~var1, ~var2, ~var3])
        if not (node_00.is_terminal or node_01.is_terminal) :
            solver.add_clause([~var1, ~var2, ~var4])
        if not (node_10.is_terminal or node_11.is_terminal) :
            solver.add_clause([~var1, ~var3, ~var4])
        if not (node_01.is_terminal or node_11.is_terminal) :
            solver.add_clause([~var2, ~var3, ~var4])


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
    # これをxy方向に対して行う．
    def make_wshape_constraint(self) :
        graph = self.__graph
        for node in graph.node_list :
            self.__wshape_sub(node, 1, 3)
            self.__wshape_sub(node, 3, 1)

    ## @brief make_wshape_constraint() の下請け関数
    def __wshape_sub(self, node_00, dir1, dir2) :
        edge_h1 = node_00.edge(dir1)
        if edge_h1 == None :
            return
        node_10 = edge_h1.alt_node(node_00)
        if node_10.is_terminal :
            return

        edge_h2 = node_10.edge(dir1)
        if edge_h2 == None :
            return
        node_20 = edge_h2.alt_node(node_10)

        edge_v1 = node_00.edge(dir2)
        if edge_v1 == None :
            return
        edge_v2 = node_20.edge(dir2)

        node_01 = edge_v1.alt_node(node_00)
        node_21 = edge_v2.alt_node(node_20)

        edge_h3 = node_01.edge(dir1)
        node_11 = edge_h3.alt_node(node_01)
        if node_11.is_terminal :
            return

        edge_h4 = node_11.edge(dir1)

        solver = self.__solver
        var1 = self.__edge_var(edge_v1)
        var4 = self.__edge_var(edge_v2)
        if not (node_00.is_terminal or node_20.is_terminal) :
            var2 = self.__edge_var(edge_h1)
            var3 = self.__edge_var(edge_h2)
            z1_edge = node_11.z1_edge
            z2_edge = node_11.z2_edge
            if z1_edge == None or z2_edge == None :
                solver.add_clause([~var1, ~var2, ~var3, ~var4])
            else :
                cvar1 = self.__edge_var(z1_edge)
                solver.add_clause([ cvar1, ~var1, ~var2, ~var3, ~var4])
        if not (node_01.is_terminal or node_21.is_terminal) :
            var2 = self.__edge_var(edge_h3)
            var3 = self.__edge_var(edge_h4)
            z1_edge = node_10.z1_edge
            z2_edge = node_10.z2_edge
            if z1_edge == None or z2_edge == None :
                solver.add_clause([~var1, ~var2, ~var3, ~var4])
            else :
                cvar1 = self.__edge_var(z1_edge)
                solver.add_clause([ cvar1, ~var1, ~var2, ~var3, ~var4])


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
    # これを3方向に対して行う．
    def make_w2shape_constraint(self) :
        graph = self.__graph
        for node in graph.node_list :
            self.__w2shape_sub(node, 1, 3)
            self.__w2shape_sub(node, 3, 1)
            self.__w2shape_sub(node, 1, 5)
            self.__w2shape_sub(node, 5, 1)
            self.__w2shape_sub(node, 3, 5)
            self.__w2shape_sub(node, 5, 3)

    ## @brief make_w2shape_constraint() の下請け関数
    def __w2shape_sub(self, node_00, dir1, dir2) :
        edge_h1 = node_00.edge(dir1)
        if edge_h1 == None :
            return
        node_10 = edge_h1.alt_node(node_00)
        if node_10.is_terminal :
            return

        edge_h2 = node_10.edge(dir1)
        if edge_h2 == None :
            return
        node_20 = edge_h2.alt_node(node_10)
        if node_20.is_terminal :
            return

        edge_h3 = node_20.edge(dir1)
        if edge_h3 == None :
            return
        node_30 = edge_h3.alt_node(node_20)

        edge_v1 = node_00.edge(dir2)
        if edge_v1 == None :
            return
        node_01 = edge_v1.alt_node(node_00)

        edge_v2 = node_30.edge(dir2)

        edge_h4 = node_01.edge(dir1)
        node_11 = edge_h4.alt_node(node_01)
        if node_11.is_terminal :
            return

        edge_h5 = node_11.edge(dir1)
        node_21 = edge_h5.alt_node(node_11)
        if node_21.is_terminal :
            return

        edge_h6 = node_21.edge(dir1)

        node_31 = edge_h6.alt_node(node_21)

        solver = self.__solver
        var_v1 = self.__edge_var(edge_v1)
        var_v2 = self.__edge_var(edge_v2)
        if not (node_00.is_terminal or node_30.is_terminal) :
            var_h1 = self.__edge_var(edge_h1)
            var_h2 = self.__edge_var(edge_h2)
            var_h3 = self.__edge_var(edge_h3)
            solver.add_clause([~var_v1, ~var_v2, ~var_h1, ~var_h2, ~var_h3])
        if not (node_01.is_terminal or node_31.is_terminal) :
            var_h4 = self.__edge_var(edge_h4)
            var_h5 = self.__edge_var(edge_h5)
            var_h6 = self.__edge_var(edge_h6)
            solver.add_clause([~var_v1, ~var_v2, ~var_h4, ~var_h5, ~var_h6])

    ## @brief L字型制約を作る．
    ##
    ## node_00 -- edge1 -- node_10
    ##    |                   |
    ##    |                   |
    ##  edge2               edge?
    ##    |                   |
    ##    |                   |
    ## node_01 -- edge? -- node_11 -- edge3
    ##                        |
    ##                        |
    ##                      edge4
    ##
    ## edge1, edge2 の経路が使えるのは node_11 が終端かビアか空き(slack = 1)か
    ## edge3, edge4 の経路がある時のみ．
    def make_lshape_constraint(self) :
        graph = self.__graph
        for node in graph.node_list :
            self.__lshape_sub(node, 1, 3)
            self.__lshape_sub(node, 0, 3)
            self.__lshape_sub(node, 1, 2)
            self.__lshape_sub(node, 0, 2)

    def __lshape_sub(self, node_00, dir1, dir2) :
        edge1 = node_00.edge(dir1)
        edge2 = node_00.edge(dir2)
        if edge1 == None or edge2 == None :
            return

        node_10 = edge1.alt_node(node_00)
        node_01 = edge2.alt_node(node_00)
        node_11 = node_10.edge(dir2).alt_node(node_10)
        if node_11.is_terminal :
            return

        solver = self.__solver
        edge3 = node_11.edge(dir1)
        edge4 = node_11.edge(dir2)
        evar1 = self.__edge_var(edge1)
        evar2 = self.__edge_var(edge2)
        if edge3 != None and edge4 != None :
            evar3 = self.__edge_var(edge3)
            evar4 = self.__edge_var(edge4)
            z1_edge = node_11.z1_edge
            z2_edge = node_11.z2_edge
            if z1_edge == None or z2_edge == None :
                solver.add_clause([~evar1, ~evar2,  evar3])
                solver.add_clause([~evar1, ~evar2,  evar4])
            else :
                z1_var = self.__edge_var(z1_edge)
                solver.add_clause([~evar1, ~evar2,  z1_var,  evar3])
                solver.add_clause([~evar1, ~evar2,  z1_var,  evar4])
        else :
            z1_edge = node_11.z1_edge
            z2_edge = node_11.z2_edge
            if z1_edge == None or z2_edge == None :
                solver.add_clause([~evar1,  ~evar2])
            else :
                z1_var = self.__edge_var(z1_edge)
                solver.add_clause([~evar1,  ~evar2,  z1_var])

    ## @brief 問題を解く．
    ## @return result, solution を返す．
    ##
    ## - result は 'OK', 'NG', 'Abort' の3種類
    ## - solution はナンバーリンクの解
    def solve(self) :
        stat, model = self.__solver.solve()
        if stat == Bool3.TRUE :
            solution = self.__decode_model(model)
            return 'OK', solution
        elif stat == Bool3.FALSE :
            return 'NG', None
        elif stat == Bool3.UNKNOWN :
            return 'Abort', None


    ## @brief SATモデルから解(NlSolution)を作る．
    def __decode_model(self, model) :
        self.__dump_model(model)
        graph = self.__graph
        solution = NlSolution()
        solution.set_size(graph.width, graph.height, graph.depth)
        for net_id in range(0, graph.net_num) :
            print('Processing Net#{}'.format(net_id))
            start, end = graph.terminal_node_pair(net_id)
            prev = None
            node = start
            while node != end :
                print(node.str())
                solution.set_val(node.x, node.y, node.z, net_id + 1)
                next = None
                # 未処理かつ選ばれている枝を探す．
                for edge in node.edge_list :
                    elit = self.__edge_var(edge)
                    evar = elit.varid()
                    if model[evar.val()] != Bool3.TRUE :
                        continue
                    node1 = edge.alt_node(node)
                    if node1 == prev :
                        continue
                    next = node1
                assert next != None
                prev = node
                node = next
            solution.set_val(node.x, node.y, node.z, net_id + 1)

        return solution

    def __dump_model(self, model) :
        graph = self.__graph
        w = graph.width
        h = graph.height
        d = graph.depth
        for z in range(0, d) :
            print('LAYER#{}'.format(z + 1))
            for y in range(0, h) :
                for x in range(0, w) :
                    node = graph.node(x, y, z)
                    lvar_list = self.__node_vars_list[node.id]
                    label = 0
                    for i, lvar in enumerate(lvar_list) :
                        if model[lvar.varid().val()] == Bool3.TRUE :
                            label += (1 << i)
                    print(' {:2d}'.format(label), end='')
                    if x < w - 1 :
                        edge = node.x2_edge
                        assert edge != None
                        evar = self.__edge_var(edge)
                        if model[evar.varid().val()] == Bool3.TRUE :
                            print(' - ', end='')
                        else :
                            print('   ', end='')
                print('')
                if y == h - 1 :
                    continue
                for x in range(0, w) :
                    node = graph.node(x, y, z)
                    edge = node.y2_edge
                    assert edge != None
                    evar = self.__edge_var(edge)
                    if model[evar.varid().val()] == Bool3.TRUE :
                        print(' |    ', end='')
                    else :
                        print('      ', end='')
                print('')
            print('')


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
    def __make_edge_constraint(self, node, no_slack) :
        graph = self.__graph

        # node に接続している枝の変数のリスト
        evar_list = [self.__edge_var_list[edge.id] for edge in node.edge_list]

        if node.is_terminal :
            # node が終端の場合

            # ただ一つの枝が選ばれる．
            self.__make_one_hot(evar_list)

            # 同時にラベルの変数を固定する．
            self.__make_label_constraint(node, node.terminal_id)
        else :
            if no_slack :
                # 常に２個の枝が選ばれる．
                self.__make_two_hot(evar_list)
            else :
                # ０個か２個の枝が選ばれる．
                self.__make_zero_or_two_hot(evar_list)


    ## @brief 枝の両端のノードのラベルに関する制約を作る．
    # @param[in] edge 対象の枝
    #
    # 具体的にはその枝が選ばれているとき両端のノードのラベルは等しい
    def __make_adj_nodes_constraint(self, edge) :
        evar = self.__edge_var_list[edge.id]
        nvar_list1 = self.__node_vars_list[edge.node1.id]
        nvar_list2 = self.__node_vars_list[edge.node2.id]
        n = len(nvar_list1)
        for i in range(0, n) :
            nvar1 = nvar_list1[i]
            nvar2 = nvar_list2[i]
            self.__make_conditional_equal(evar, nvar1, nvar2)


    ## @brief ラベル値を固定する制約を作る．
    # @param[in] node 対象のノード
    # @param[in] net_id 固定する線分番号
    def __make_label_constraint(self, node, net_id) :
        lvar_list = self.__node_vars_list[node.id]
        for i, lvar in enumerate(lvar_list) :
            if (1 << i) & (net_id + 1) :
                tmp_lit = lvar
            else :
                tmp_lit = ~lvar
            self.__solver.add_clause([tmp_lit])


    ## @brief 条件付きでラベル値を固定する制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] node 対象のノード
    # @param[in] net_id 固定する線分番号
    def __make_conditional_label_constraint(self, cvar, node, net_id) :
        lvar_list = self.__node_vars_list[node.id]
        for i, lvar in enumerate(lvar_list) :
            if (1 << i) & (net_id + 1) :
                self.__solver.add_clause([~cvar, lvar])
            else :
                self.__solver.add_clause([~cvar, ~lvar])


    ## @brief 枝に対する変数番号を返す．
    # @param[in] edge 対象の枝
    def __edge_var(self, edge) :
        return self.__edge_var_list[edge.id]


    ## @brief 条件付きでリストの中の変数がすべて False となる制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] var_list 対象の変数のリスト
    def __make_conditional_zero_hot(self, cvar, var_list) :
        solver = self.__solver
        for var in var_list :
            solver.add_clause([~cvar, ~var])


    ## @brief リストの中の変数が1つだけ True となる制約を作る．
    # @param[in] var_list 対象の変数のリスト
    def __make_one_hot(self, var_list) :
        n = len(var_list)
        solver = self.__solver
        # 要素数で場合分け
        if n == 2 :
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause([~var0, ~var1])
            solver.add_clause([ var0,  var1])
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause([~var0, ~var1       ])
            solver.add_clause([~var0,        ~var2])
            solver.add_clause([       ~var1, ~var2])
            solver.add_clause([ var0,  var1,  var2])
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause([~var0, ~var1              ])
            solver.add_clause([~var0,        ~var2       ])
            solver.add_clause([~var0,               ~var3])
            solver.add_clause([       ~var1, ~var2       ])
            solver.add_clause([       ~var1,        ~var3])
            solver.add_clause([              ~var2, ~var3])
            solver.add_clause([ var0,  var1,  var2,  var3])
        else :
            # 一般形
            for i in range(0, n - 1) :
                var0 = var_list[i]
                for j in range(i + 1, n) :
                    var1 = var_list[j]
                    solver.add_clause([~var0, ~var1])
            solver.add_clause(var_list)


    ## @brief 条件付きでリストの中の変数が1つだけ True となる制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] var_list 対象の変数のリスト
    def __make_conditional_one_hot(self, cvar, var_list) :
        solver = self.__solver
        n = len(var_list)
        # 要素数で場合分け
        if n == 2 :
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause([~cvar, ~var0, ~var1])
            solver.add_clause([~cvar,  var0,  var1])
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause([~cvar, ~var0, ~var1       ])
            solver.add_clause([~cvar, ~var0,        ~var2])
            solver.add_clause([~cvar,        ~var1, ~var2])
            solver.add_clause([~cvar,  var0,  var1,  var2])
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause([~cvar, ~var0, ~var1              ])
            solver.add_clause([~cvar, ~var0,        ~var2       ])
            solver.add_clause([~cvar, ~var0,               ~var3])
            solver.add_clause([~cvar,        ~var1, ~var2       ])
            solver.add_clause([~cvar,        ~var1,        ~var3])
            solver.add_clause([~cvar,               ~var2, ~var3])
            solver.add_clause([~cvar,  var0,  var1,  var2,  var3])
        else :
            # 一般形
            tmp_list = []
            tmp_list.append(~cvar)
            for i in range(0, n - 1) :
                var0 = var_list[i]
                tmp_list.append(var0)
                for j in range(i + 1, n) :
                    var1 = var_list[j]
                    solver.add_clause([~cvar, ~var0, ~var1])
            solver.add_clause(tmp_list)


    ## @brief リストの中の変数が2個 True になるという制約
    # @param[in] var_list 対象の変数のリスト
    def __make_two_hot(self, var_list) :
        solver = self.__solver
        n = len(var_list)
        # 要素数で場合分け
        # 基本的には
        # - 3つ以上の変数が同時に True にならない．
        # - n - 1 個以上の変数が同時に False にならない．
        # という条件を組み合わせる．
        if n == 2 :
            # いつも選ばれる．
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause([var0])
            solver.add_clause([var1])
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause([~var0, ~var1, ~var2])
            solver.add_clause([ var0,  var1       ])
            solver.add_clause([ var0,         var2])
            solver.add_clause([        var1,  var2])
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause([~var0, ~var1, ~var2       ])
            solver.add_clause([~var0, ~var1,        ~var3])
            solver.add_clause([~var0,        ~var2, ~var3])
            solver.add_clause([       ~var1, ~var2, ~var3])
            solver.add_clause([ var0,  var1,  var2       ])
            solver.add_clause([ var0,  var1,         var3])
            solver.add_clause([ var0,         var2,  var3])
            solver.add_clause([        var1,  var2,  var3])
        elif n == 5 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            var4 = var_list[4]
            solver.add_clause([~var0, ~var1, ~var2              ])
            solver.add_clause([~var0, ~var1,        ~var3       ])
            solver.add_clause([~var0, ~var1,               ~var4])
            solver.add_clause([~var0,        ~var2, ~var3       ])
            solver.add_clause([~var0,        ~var2,        ~var4])
            solver.add_clause([~var0,               ~var3, ~var4])
            solver.add_clause([       ~var1, ~var2, ~var3       ])
            solver.add_clause([       ~var1, ~var2,        ~var4])
            solver.add_clause([       ~var1,        ~var3, ~var4])
            solver.add_clause([              ~var2, ~var3, ~var4])
            solver.add_clause([ var0,  var1,  var2,  var3       ])
            solver.add_clause([ var0,  var1,  var2,         var4])
            solver.add_clause([ var0,  var1,         var3,  var4])
            solver.add_clause([ var0,         var2,  var3,  var4])
            solver.add_clause([        var1,  var2,  var3,  var4])
        elif n == 6 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            var4 = var_list[4]
            var5 = var_list[5]
            solver.add_clause([~var0, ~var1, ~var2                     ])
            solver.add_clause([~var0, ~var1,        ~var3              ])
            solver.add_clause([~var0, ~var1,               ~var4       ])
            solver.add_clause([~var0, ~var1,                      ~var5])
            solver.add_clause([~var0,        ~var2, ~var3              ])
            solver.add_clause([~var0,        ~var2,        ~var4       ])
            solver.add_clause([~var0,        ~var2,               ~var5])
            solver.add_clause([~var0,               ~var3, ~var4       ])
            solver.add_clause([~var0,               ~var3,        ~var5])
            solver.add_clause([~var0,                      ~var4, ~var5])
            solver.add_clause([       ~var1, ~var2, ~var3              ])
            solver.add_clause([       ~var1, ~var2,        ~var4       ])
            solver.add_clause([       ~var1, ~var2,               ~var5])
            solver.add_clause([       ~var1,        ~var3, ~var4       ])
            solver.add_clause([       ~var1,        ~var3,        ~var5])
            solver.add_clause([       ~var1,               ~var4, ~var5])
            solver.add_clause([              ~var2, ~var3, ~var4       ])
            solver.add_clause([              ~var2, ~var3,        ~var5])
            solver.add_clause([              ~var2,        ~var4, ~var5])
            solver.add_clause([                     ~var3, ~var4, ~var5])
            solver.add_clause([ var0,  var1,  var2,  var3,  var4       ])
            solver.add_clause([ var0,  var1,  var2,  var3,         var5])
            solver.add_clause([ var0,  var1,  var2,         var4,  var5])
            solver.add_clause([ var0,  var1,         var3,  var4,  var5])
            solver.add_clause([ var0,         var2,  var3,  var4,  var5])
            solver.add_clause([        var1,  var2,  var3,  var4,  var5])
        else :
            assert False


    ## @brief リストの中の変数が0個か2個 True になるという制約
    # @param[in] var_list 対象の変数のリスト
    def __make_zero_or_two_hot(self, var_list) :
        solver = self.__solver
        n = len(var_list)
        # 要素数で場合分け
        # 基本的な考え方は
        # - 3つ以上の変数が同時に True にならない．
        # - True の変数が1つだけという組み合わせはない．
        # という条件を組み合わせる．
        if n == 2 :
            var0 = var_list[0]
            var1 = var_list[1]
            solver.add_clause([ var0, ~var1])
            solver.add_clause([~var0,  var1])
        elif n == 3 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            solver.add_clause([~var0, ~var1, ~var2])
            solver.add_clause([ var0,  var1, ~var2])
            solver.add_clause([ var0, ~var1,  var2])
            solver.add_clause([~var0,  var1,  var2])
        elif n == 4 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            solver.add_clause([~var0, ~var1, ~var2       ])
            solver.add_clause([~var0, ~var1,        ~var3])
            solver.add_clause([~var0,        ~var2, ~var3])
            solver.add_clause([       ~var1, ~var2, ~var3])
            solver.add_clause([ var0,  var1,  var2, ~var3])
            solver.add_clause([ var0,  var1, ~var2,  var3])
            solver.add_clause([ var0, ~var1,  var2,  var3])
            solver.add_clause([~var0,  var1,  var2,  var3])
        elif n == 5 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            var4 = var_list[4]
            solver.add_clause([~var0, ~var1, ~var2              ])
            solver.add_clause([~var0, ~var1,        ~var3       ])
            solver.add_clause([~var0, ~var1,               ~var4])
            solver.add_clause([~var0,        ~var2, ~var3       ])
            solver.add_clause([~var0,        ~var2,        ~var4])
            solver.add_clause([~var0,               ~var3, ~var4])
            solver.add_clause([       ~var1, ~var2, ~var3       ])
            solver.add_clause([       ~var1, ~var2,        ~var4])
            solver.add_clause([       ~var1,        ~var3, ~var4])
            solver.add_clause([              ~var2, ~var3, ~var4])
            solver.add_clause([ var0,  var1,  var2,  var3, ~var4])
            solver.add_clause([ var0,  var1,  var2, ~var3,  var4])
            solver.add_clause([ var0,  var1, ~var2,  var3,  var4])
            solver.add_clause([ var0, ~var1,  var2,  var3,  var4])
            solver.add_clause([~var0,  var1,  var2,  var3,  var4])
        elif n == 6 :
            var0 = var_list[0]
            var1 = var_list[1]
            var2 = var_list[2]
            var3 = var_list[3]
            var4 = var_list[4]
            var5 = var_list[5]
            solver.add_clause([~var0, ~var1, ~var2                     ])
            solver.add_clause([~var0, ~var1,        ~var3              ])
            solver.add_clause([~var0, ~var1,               ~var4       ])
            solver.add_clause([~var0, ~var1,                      ~var5])
            solver.add_clause([~var0,        ~var2, ~var3              ])
            solver.add_clause([~var0,        ~var2,        ~var4       ])
            solver.add_clause([~var0,        ~var2,               ~var5])
            solver.add_clause([~var0,               ~var3, ~var4       ])
            solver.add_clause([~var0,               ~var3,        ~var5])
            solver.add_clause([~var0,                      ~var4, ~var5])
            solver.add_clause([       ~var1, ~var2, ~var3              ])
            solver.add_clause([       ~var1, ~var2,        ~var4       ])
            solver.add_clause([       ~var1, ~var2,               ~var5])
            solver.add_clause([       ~var1,        ~var3, ~var4       ])
            solver.add_clause([       ~var1,        ~var3,        ~var5])
            solver.add_clause([       ~var1,               ~var4, ~var5])
            solver.add_clause([              ~var2, ~var3, ~var4       ])
            solver.add_clause([              ~var2, ~var3,        ~var5])
            solver.add_clause([              ~var2,        ~var4, ~var5])
            solver.add_clause([                     ~var3, ~var4, ~var5])
            solver.add_clause([ var0,  var1,  var2,  var3,  var4, ~var5])
            solver.add_clause([ var0,  var1,  var2,  var3, ~var4,  var5])
            solver.add_clause([ var0,  var1,  var2, ~var3,  var4,  var5])
            solver.add_clause([ var0,  var1, ~var2,  var3,  var4,  var5])
            solver.add_clause([ var0, ~var1,  var2,  var3,  var4,  var5])
            solver.add_clause([~var0,  var1,  var2,  var3,  var4,  var5])
        else :
            assert False


    ## @brief 条件付きで２つの変数が等しくなるという制約を作る．
    # @param[in] cvar 条件を表す変数
    # @param[in] var1, var2 対象の変数
    def __make_conditional_equal(self, cvar, var1, var2) :
        solver = self.__solver
        solver.add_clause([~cvar, ~var1,  var2])
        solver.add_clause([~cvar,  var1, ~var2])

# end-of-class NlCnfEncoder
