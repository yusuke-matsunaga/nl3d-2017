#! /usr/bin/env python3

### @file v2017/cnfencoder.py
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

    ### @brief 基本的な制約を作る．
    ### @param[in] no_slack すべてのマス目を使う制約を入れるとき True にするフラグ
    def make_base_constraint(self, no_slack) :
        solver = self.__solver
        graph = self.__graph

        # 枝に対応する変数を作る．
        # 結果は edge_var_list に格納する．
        # __edge_var_list[edge.id] に edge に対応する変数が入る．
        # 実際にはその変数に対応するリテラルを入れる．
        self.__edge_var_list = [solver.new_variable() for edge in graph.edge_list]

        # 節点のラベルを表す変数のリストを作る．
        # 節点のラベルは log2(nn + 1) 個の変数で表す(binaryエンコーディング)
        # 結果は __node_vars_list に格納する．
        # __node_vars_list[node.id] に node に対応する変数のリストが入る．
        # 実際にはその変数に対応するリテラルを入れる．
        nn = graph.net_num
        if self.__binary_encoding :
            nn_log2 = math.ceil(math.log2(nn + 1))
            self.__node_vars_list = [[solver.new_variable() for i in range(0, nn_log2)] \
                                     for node in graph.node_list]
        else :
            self.__node_vars_list = [[solver.new_variable() for i in range(0, nn)] \
                                     for node in graph.node_list]

        if not no_slack :
            # 節点が使われている時 True になる変数を用意する．
            self.__uvar_list = [solver.new_variable() for node in graph.node_list]

        # 各節点に対して隣接する枝の条件を作る．
        for node in graph.node_list :
            self.__make_edge_constraint(node, no_slack)

        # 枝が選択された時にその両端のノードのラベルが等しくなるという制約を作る．
        for edge in graph.edge_list :
            self.__make_adj_nodes_constraint(edge)

        # U字制約を作る．
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
    ###
    ### これを3方向で行う．
    def make_ushape_constraint(self) :
        graph = self.__graph
        solver = self.__solver
        for edge1, edge2, edge3, edge4 in graph.square_edges :
            var1 = self.edge_var(edge1)
            var2 = self.edge_var(edge2)
            var3 = self.edge_var(edge3)
            var4 = self.edge_var(edge4)
            solver.add_at_most_two([var1, var2, var3, var4])

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
        var1 = self.edge_var(edge_v1)
        var4 = self.edge_var(edge_v2)
        if not (node_00.is_terminal or node_20.is_terminal) :
            var2 = self.edge_var(edge_h1)
            var3 = self.edge_var(edge_h2)
            z1_edge = node_11.z1_edge
            z2_edge = node_11.z2_edge
            if z1_edge == None or z2_edge == None :
                solver.add_clause([~var1, ~var2, ~var3, ~var4])
            else :
                cvar1 = self.edge_var(z1_edge)
                solver.add_clause([ cvar1, ~var1, ~var2, ~var3, ~var4])
        if not (node_01.is_terminal or node_21.is_terminal) :
            var2 = self.edge_var(edge_h3)
            var3 = self.edge_var(edge_h4)
            z1_edge = node_10.z1_edge
            z2_edge = node_10.z2_edge
            if z1_edge == None or z2_edge == None :
                solver.add_clause([~var1, ~var2, ~var3, ~var4])
            else :
                cvar1 = self.edge_var(z1_edge)
                solver.add_clause([ cvar1, ~var1, ~var2, ~var3, ~var4])

    ## @brief L字型制約を作る．
    ##
    ## node_00 -- edge1 -- node_10
    ##    |                   |
    ##    |                   |
    ##  edge2               edge?
    ##    |                   |
    ##    |                   |
    ## node_01 -- edge? -- node_11
    ##
    ## edge1, edge2 の経路が使えるのは node_00 の南東方向に終端かビアがある時か，
    ## node_00 の南と東に同じ線分番号の終端かビアがある時
    def make_lshape_constraint(self) :
        graph = self.__graph
        w1 = graph.width - 1
        h1 = graph.height - 1
        for node in graph.node_list :
            if node.is_terminal :
                continue
            if node.x == 0 or node.x == w1 or node.y == 0 or node.y == h1 :
                # 外周部には制約を設けない．
                continue
            self.__lshape_sub(node, -1, -1)
            self.__lshape_sub(node, -1,  1)
            self.__lshape_sub(node,  1, -1)
            self.__lshape_sub(node,  1,  1)

    def __lshape_sub(self, node_00, dx, dy) :
        dir1 = (1 - dx) // 2
        edge1 = node_00.edge(dir1)
        if edge1 == None :
            return
        dir2 = (1 - dy) // 2
        edge2 = node_00.edge(dir2)
        if edge2 == None :
            return

        graph = self.__graph
        w = graph.width
        h = graph.height
        x0 = node_00.x
        y0 = node_00.y
        z0 = node_00.z
        rx = w - x0 if dx > 0 else x0 + 1
        ry = h - y0 if dy > 0 else y0 + 1

        # X軸方向に端子があるかを調べる．
        def xcheck(graph, x0, y0, z0, dx, rx) :
            for i in range(1, rx) :
                x1 = x0 + i * dx
                node = graph.node(x1, y0, z0)
                if node.is_terminal :
                    return True, node.terminal_id
            return False, 0

        # Y軸方向に端子があるかを調べる．
        def ycheck(graph, x0, y0, z0, dy, ry) :
            for i in range(1, ry) :
                y1 = y0 + i * dy
                node = graph.node(x0, y1, z0)
                if node.is_terminal :
                    return True, node.terminal_id
            return False, 0

        xcheck, xnet_id = xcheck(graph, x0, y0, z0, dx, rx)
        ycheck, ynet_id = ycheck(graph, x0, y0, z0, dy, ry)
        if xcheck and ycheck and (xnet_id == ynet_id) :
            # X軸方向，Y軸方向ともに同じネット番号の端子がある場合は制約を付けない．
            return

        r = rx if rx < ry else ry
        for i in range(1, r) :
            x1 = x0 + i * dx
            y1 = y0 + i * dy
            node = graph.node(x1, y1, z0)
            if node.is_terminal :
                # 45度方向に端子がある場合にも制約を付けない．
                return

        # 上記のスクリーニングで引っかからない場合にはL字制約をつける．
        evar1 = self.edge_var(edge1)
        evar2 = self.edge_var(edge2)
        self.__solver.add_clause([~evar1, ~evar2])


    ## @brief Y字経路を禁止する制約を生成する．
    ##
    ##    |                   |                   |
    ##  edge?               edge3               edge?
    ##    |                   |                   |
    ##    |                   |                   |
    ## node_00 -- edge? -- node_10 -- edge? -- node_20
    ##    |                   |                   |
    ##    |                   |                   |
    ##  edge1               edge?               edge2
    ##    |                   |                   |
    ##    |                   |                   |
    ## node_01 -- edge? -- node_11 -- edge? -- node_21
    ##    |                   |                   |
    ##    |                   |                   |
    ##  edge?               edge4               edge?
    ##    |                   |                   |
    ##
    ## 共通な条件: node_10, node_11 が共に終端，ビアでない．
    ##            edge1 と edge2 が選ばれている．
    ## 1: node_10 が空きでなければ edge3 は選ばれる．
    ## 2: node_11 が空きでなければ edge4 は選ばれる．
    ##
    ## edge3, edge4 がない場合は node_10, node_11 が空きでなければならない．
    def make_yshape_constraint(self) :
        graph = self.__graph
        for node in graph.node_list :
            if node.is_terminal :
                continue
            self.__yshape_sub(node, 0, 2)
            self.__yshape_sub(node, 2, 0)

    def __yshape_sub(self, node_10, dir1, dir3) :
        solver = self.__solver

        node_11 = node_10.adj_node(dir3)
        if node_11 == None or node_11.is_terminal :
            return

        node_00 = node_10.adj_node(dir1)
        node_20 = node_10.adj_node(dir1 + 1)
        if node_00 == None or node_20 == None :
            return

        edge1 = node_00.edge(dir3)
        edge2 = node_20.edge(dir3)
        evar1 = self.edge_var(edge1)
        evar2 = self.edge_var(edge2)

        uvar0 = self.node_uvar(node_10)
        edge3 = node_10.edge(dir3 + 1)
        if edge3 == None :
            solver.add_clause([~evar1, ~evar2, ~uvar0])
        else :
            evar3 = self.edge_var(edge3)
            solver.add_clause([~evar1, ~evar2,  evar3])

        uvar1 = self.node_uvar(node_11)
        edge4 = node_11.edge(dir3)
        if edge4 == None :
            solver.add_clause([~evar1, ~evar2, ~uvar1])
        else :
            evar4 = self.edge_var(edge4)
            solver.add_clause([~evar1, ~evar2,  evar4])

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

    ## @brief SATモデルから経路を作る．
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
                elit = self.edge_var(edge)
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

        return route

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
                    if self.__binary_encoding :
                        label = 0
                        for i, lvar in enumerate(lvar_list) :
                            if model[lvar.varid().val()] == Bool3.TRUE :
                                label += (1 << i)
                        for i, lvar in enumerate(lvar_list) :
                            if model[lvar.varid().val()] == Bool3.TRUE :
                                label = i
                    print(' {:2d}'.format(label), end='')
                    if x < w - 1 :
                        edge = node.x2_edge
                        assert edge != None
                        evar = self.edge_var(edge)
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
                    evar = self.edge_var(edge)
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
                # uvar が True の時は2つの枝が選ばれる．
                # そうでなければ選ばれない．
                uvar = self.node_uvar(node)
                solver.add_at_most_two(evar_list)
                solver.add_at_least_two(evar_list, cvar_list = [uvar])
                for evar in evar_list :
                    solver.add_clause([ uvar, ~evar])

    ## @brief 枝の両端のノードのラベルに関する制約を作る．
    # @param[in] edge 対象の枝
    #
    # 具体的にはその枝が選ばれているとき両端のノードのラベルは等しい
    def __make_adj_nodes_constraint(self, edge) :
        solver = self.__solver
        evar = self.__edge_var_list[edge.id]
        var_list1 = self.__node_vars_list[edge.node1.id]
        var_list2 = self.__node_vars_list[edge.node2.id]
        n = len(var_list1)
        for i in range(0, n) :
            var1 = var_list1[i]
            var2 = var_list2[i]
            solver.add_eq_rel(var1, var2, cvar_list = [evar])
        if self.__binary_encoding :
            pass
        else :
            # cvar が False なら var_list1 と var_list2 は等しくない．
            for i in range(0, n) :
                var1 = var_list1[i]
                var2 = var_list2[i]
                solver.add_clause([ evar, ~var1, ~var2])

    ## @brief ラベル値を固定する制約を作る．
    # @param[in] node 対象のノード
    # @param[in] net_id 固定する線分番号
    def __make_label_constraint(self, node, net_id) :
        lvar_list = self.__node_vars_list[node.id]
        if self.__binary_encoding :
            for i, lvar in enumerate(lvar_list) :
                if (1 << i) & (net_id + 1) :
                    tmp_lit =  lvar
                else :
                    tmp_lit = ~lvar
                self.__solver.add_clause([tmp_lit])
        else :
            for i, lvar in enumerate(lvar_list) :
                if i == net_id :
                    tmp_lit =  lvar
                else :
                    tmp_lit = ~lvar
                self.__solver.add_clause([tmp_lit])

    ## @brief ノードに対する uvar を返す．
    def node_uvar(self, node) :
        return self.__uvar_list[node.id]

    ## @brief 枝に対する変数番号を返す．
    # @param[in] edge 対象の枝
    def edge_var(self, edge) :
        return self.__edge_var_list[edge.id]

# end-of-class CnfEncoder
