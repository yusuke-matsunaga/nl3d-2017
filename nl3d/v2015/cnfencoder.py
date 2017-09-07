#! /usr/bin/env python3

### @file v2015/cnfencoder.py
### @brief CnfEncoder の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import math
from nl3d.router import Router
from pym_sat import SatSolver, Bool3


### @brief 問題を表すCNF式を生成するクラス
###
### 内部に Graph の要素に対する変数の割り当て情報を持つ．
class CnfEncoder :

    ### @brief 初期化
    ### @param[in] graph 問題を表すグラフ
    ### @param[in] solver_type SATソルバの型を表す文字列
    ### @param[in] binary_encoding ノードラベル変数を２進符号化する時 True にするフラグ
    ###
    ### ここではSATの変数の割当のみ行う．
    def __init__(self, graph, solver_type, binary_encoding) :
        solver = SatSolver(solver_type)
        self.__graph = graph
        self.__solver = solver
        self.__binary_encoding = binary_encoding
        nn = graph.net_num

        # 枝に対応する変数を作る．
        # 結果は __edge_var_list に格納する．
        # __edge_var_list[edge.id] に edge に対応する変数が入る．
        self.__edge_var_list = [solver.new_variable() for edge in graph.edge_list]

        # 節点のラベルを表す変数のリストを作る．
        # 節点のラベルは log2(nn + 1) 個の変数で表す(binaryエンコーディング)
        # 結果は node_vars_list に格納する．
        # _node_vars_list[node.id] に node に対応する変数のリストが入る．
        if self.__binary_encoding :
            nn_log2 = math.ceil(math.log2(nn + 1))
            self.__node_vars_list = [[solver.new_variable() for i in range(0, nn_log2)] \
                                     for node in graph.node_list]
        else :
            self.__node_vars_list = [[solver.new_variable() for i in range(0, nn)] \
                                     for node in graph.node_list]

    ### @brief 基本的な制約を作る．
    ### @param[in] no_slack すべてのマス目を使う制約を入れるとき True にするフラグ
    def make_base_constraint(self, no_slack) :
        solver = self.__solver
        graph = self.__graph

        if not no_slack :
            # 節点が使われている時 True になる変数を用意する．
            self.__uvar_list = [solver.new_variable() for node in graph.node_list]

        # 各節点に対して隣接する枝の条件を作る．
        for node in graph.node_list :
            self.__make_edge_constraint(node, no_slack)

        # 枝が選択された時にその両端のノードのラベルが等しくなるという制約を作る．
        for edge in graph.edge_list :
            self.__make_adj_nodes_constraint(edge)

        self.make_ushape_constraint()

    ### @brief U字(コの字)制約を作る．
    ###
    ### node_00 -- edge1 -- node_10
    ###    |                   |
    ###    |                   |
    ###  edge2               edge3
    ###    |                   |
    ###    |                   |
    ### node_01 -- edge4 -- node_11
    ###
    ### edge1, edge2, edge3, edge4 の３つ以上が同時に使われる
    ### 経路は存在しない．
    def make_ushape_constraint(self) :
        graph = self.__graph
        solver = self.__solver
        dir1 = 1
        dir2 = 3
        for node_00 in graph.node_list :
            # 変数名は上の図に対応している．
            edge1 = node_00.edge(dir1)
            edge2 = node_00.edge(dir2)
            if edge1 == None or edge2 == None :
                continue

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

            var1 = self.__edge_var(edge1)
            var2 = self.__edge_var(edge2)
            var3 = self.__edge_var(edge3)
            var4 = self.__edge_var(edge4)
            solver.add_at_most_two([var1, var2, var3, var4])

    ### @brief 2x3マスのコの字経路を禁止する制約を作る．
    ###
    ### node_00 -- edge_h1 -- node_10 -- edge_h2 -- node_20
    ###    |                     |                     |
    ###    |                     |                     |
    ### edge_v1               edge_??               edge_v2
    ###    |                     |                     |
    ###    |                     |                     |
    ### node_01 -- edge_h3 -- node_11 -- edge_h4 -- node_21
    ###
    ### 1: node_11 が終端かビアでない限り，edge_v1, edge_h1, edge_h2, edge_v2
    ###    という経路は使えない．
    ### 2: node_10 が終端化ビアでない限り，edge_v1, edge_h3, edge_h4, edge_v2
    ###    という経路は使えない．
    ###
    ### これをタテ・ヨコの２方向に対して行う．
    def make_wshape_constraint(self) :
        graph = self.__graph
        for node in graph.node_list :
            self.__wshape_sub(node, 1, 3)
            self.__wshape_sub(node, 3, 1)

    ### @brief make_wshape_constraint() の下請け関数
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
        var1 = self._edge_var(edge_v1)
        var4 = self._edge_var(edge_v2)
        if not (node_00.is_terminal or node_20.is_terminal) :
            var2 = self.__edge_var(edge_h1)
            var3 = self.__edge_var(edge_h2)
            solver.add_clause([~var1, ~var2, ~var3, ~var4])
        if not (node_01.is_terminal or node_21.is_terminal) :
            var2 = self.__edge_var(edge_h3)
            var3 = self.__edge_var(edge_h4)
            solver.add_clause([~var1, ~var2, ~var3, ~var4])

    ### @brief 2x4マスのコの字経路を禁止する制約を作る．
    ###
    ### node_00 -- edge_h1 -- node_10 -- edge_h2 -- node_20 -- edge_h3 -- node_30
    ###    |                     |                     |                     |
    ###    |                     |                     |                     |
    ### edge_v1               edge_??               edge_??               edge_v2
    ###    |                     |                     |                     |
    ###    |                     |                     |                     |
    ### node_01 -- edge_h4 -- node_11 -- edge_h5 -- node_21 -- edge_h6 -- node_31
    ###
    ### 1: node_11, node_21 が終端かビアでない限り，
    ###    edge_v1, edge_h1, edge_h2, edge_h3, edge_v2 という経路は使えない．
    ### 2: node_10, node_20 が終端かビアでない限り，
    ###    edge_v1, edge_h4, edge_h5, edge_h6, edge_v2 という経路は使えない．
    ###
    ### これをタテ・ヨコの２方向に対して行う．
    def make_w2shape_constraint(self) :
        graph = self.__graph
        solver = self.__solver
        for node_00 in graph.node_list :
            # d は方向(0: ヨコ, 1: タテ)
            for d in range(0, 2) :
                edge_h1 = node_00.lower_edge if d else node_00.x2_edge
                if edge_h1 == None :
                    continue
                node_10 = edge_h1.alt_node(node_00)
                if node_10.is_terminal :
                    continue

                edge_h2 = node_10.lower_edge if d else node_10.x2_edge
                if edge_h2 == None :
                    continue
                node_20 = edge_h2.alt_node(node_10)
                if node_20.is_terminal :
                    continue

                edge_h3 = node_20.lower_edge if d else node_20.x2_edge
                if edge_h3 == None :
                    continue
                node_30 = edge_h3.alt_node(node_20)

                edge_v1 = node_00.x2_edge if d else node_00.lower_edge
                if edge_v1 == None :
                    continue
                node_01 = edge_v1.alt_node(node_00)

                edge_v2 = node_30.x2_edge if d else node_30.lower_edge

                edge_h4 = node_01.lower_edge if d else node_01.x2_edge
                node_11 = edge_h4.alt_node(node_01)
                if node_11.is_terminal :
                    continue

                edge_h5 = node_11.lower_edge if d else node_11.x2_edge
                node_21 = edge_h5.alt_node(node_11)
                if node_21.is_terminal :
                    continue

                edge_h6 = node_21.lower_edge if d else node_21.x2_edge

                node_31 = edge_h6.alt_node(node_21)

                var_v1 = self._edge_var(edge_v1)
                var_v2 = self._edge_var(edge_v2)
                if not (node_00.is_terminal or node_30.is_terminal) :
                    var_h1 = self._edge_var(edge_h1)
                    var_h2 = self._edge_var(edge_h2)
                    var_h3 = self._edge_var(edge_h3)
                    solver.add_clause([~varf_v1, ~var_v2, ~var_h1, ~var_h2, ~var_h3])
                if not (node_01.is_terminal or node_31.is_terminal) :
                    var_h4 = self._edge_var(edge_h4)
                    var_h5 = self._edge_var(edge_h5)
                    var_h6 = self._edge_var(edge_h6)
                    solver.add_clause([~var_v1, ~var_v2, ~var_h4, ~var_h5, ~var_h6])

    ## @brief 問題を解く．
    ## @return result, solution を返す．
    ##
    ## - result は 'OK', 'NG', 'Abort' の3種類
    ## - solution はナンバーリンクの解
    def solve(self, var_limit) :
        solver = self.__solver
        print('SAT start')
        print(' # of variables: {}'.format(solver.variable_num()))
        print(' # of clauses:   {}'.format(solver.clause_num()))
        print(' # of literals:  {}'.format(solver.literal_num()))
        if var_limit > 0 and self.__solver.variable_num() > var_limit :
            print('  variable limit ({}) exceeded'.format(var_limit))
            return 'Abort', None
        stat, model = solver.solve()
        print('    end')
        if stat == Bool3.TRUE :
            verbose = False
            net_num = self.__graph.net_num
            route_list = [self.__find_route(net_id, model) for net_id in range(0, net_num)]
            router = Router(self.__graph.dimension, route_list, verbose)
            router.reroute()
            solution = router.to_solution()
            return 'OK', solution
        elif stat == Bool3.FALSE :
            return 'NG', None
        elif stat == Bool3.UNKNOWN :
            return 'Abort', None

    ### @brief SATモデルから経路を作る．
    def __find_route(self, net_id, model) :
        graph = self.__graph
        start, end = graph.terminal_node_pair(net_id)
        prev = None
        node = start
        route = []
        while True :
            route.append(node.point)
            if node == end :
                break

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
                break
            assert next != None
            prev = node
            node = next

        return route

    ### @brief ノードに接続する枝に関する制約を作る．
    ### @param[in] no_slack すべてのマス目を使う制約を入れるときに True にするフラグ
    ###
    ### 具体的には
    ### - 終端の場合
    ###   ただ一つの枝のみが選ばれる．
    ### - それ以外
    ###   全て選ばれないか2つの枝が選ばれる．
    def __make_edge_constraint(self, node, no_slack) :
        solver = self.__solver
        graph = self.__graph

        # node に接続している枝の変数のリスト
        evar_list = [self.__edge_var_list[edge.id] for edge in node.edge_list]

        if node.is_terminal :
            # node が終端の場合

            # ただ一つの枝が選ばれる．
            solver.add_exact_one(evar_list)

            # 同時にラベルの変数を固定する．
            self.__make_label_constraint(node, node.terminal_id)
        else :
            if no_slack :
                # 常に２個の枝が選ばれる．
                solver.add_exact_two(evar_list)
            else :
                # ０個か２個の枝が選ばれる．
                uvar = self.__uvar_list[node.id]
                solver.add_at_most_two(evar_list, cvar_list = [uvar])
                for evar in evar_list :
                    solver.add_clause([ uvar, ~evar])

    ### @brief 枝の両端のノードのラベルに関する制約を作る．
    ### @param[in] edge 対象の枝
    ###
    ### 具体的にはその枝が選ばれているとき両端のノードのラベルは等しい
    def __make_adj_nodes_constraint(self, edge) :
        solver = self.__solver
        evar = self.__edge_var_list[edge.id]
        nvar_list1 = self.__node_vars_list[edge.node1.id]
        nvar_list2 = self.__node_vars_list[edge.node2.id]
        n = len(nvar_list1)
        solver.set_conditional_literals([evar])
        for i in range(0, n) :
            nvar1 = nvar_list1[i]
            nvar2 = nvar_list2[i]
            solver.add_eq_rel(nvar1, nvar2)
        solver.clear_conditional_literals()

    ## @brief ラベル値を固定する制約を作る．
    # @param[in] node 対象のノード
    # @param[in] net_id 固定する線分番号
    def __make_label_constraint(self, node, net_id) :
        solver = self.__solver
        lvar_list = self.__node_vars_list[node.id]
        for i, lvar in enumerate(lvar_list) :
            if (1 << i) & (net_id + 1) :
                solver.add_clause([lvar])
            else :
                solver.add_clause([~lvar])

    ## @brief 枝に対する変数番号を返す．
    # @param[in] edge 対象の枝
    def __edge_var(self, edge) :
        return self.__edge_var_list[edge.id]

# end-of-class CnfEncoder
