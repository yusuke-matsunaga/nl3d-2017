#! /usr/bin/env python3

### @file v2016/cnfencoder.py
### @brief CnfEncoder の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import math
import time
from nl3d.point import Point
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
        self.__time0 = time.time()

    ### @brief 基本的な制約を作る．
    ### @param[in] no_slack すべてのマス目を使う制約を入れるとき True にするフラグ
    def make_base_constraint(self, no_slack, use_uvar) :
        solver = self.__solver
        graph = self.__graph

        self.__use_uvar = use_uvar

        # 枝に対応する変数を作る．
        # 結果は __edge_var_list に格納する．
        # __edge_var_list[edge.id] に edge に対応する変数が入る．
        self.__edge_var_list = [solver.new_variable() for edge in graph.edge_list]

        # 節点のラベルを表す変数のリストを作る．
        # 節点のラベルは log2(nn + 1) 個の変数で表す(binaryエンコーディング)
        # 結果は node_vars_list に格納する．
        # _node_vars_list[node.id] に node に対応する変数のリストが入る．
        nl = graph.label_num
        if self.__binary_encoding :
            nl_log2 = math.ceil(math.log2(nl + 1))
            self.__node_vars_list = [[solver.new_variable() for i in range(0, nl_log2)] \
                                     for node in graph.node_list]
        else :
            self.__node_vars_list = [[solver.new_variable() for i in range(0, nl)] \
                                     for node in graph.node_list]

        # ビアと線分の割り当てを表す変数を作る．
        # __nv_map[net_id][via_id] に net_id の線分を via_id のビアに接続する時
        # True となる変数を入れる．
        vn = graph.via_num
        nn = graph.net_num
        self.__nv_map = [[solver.new_variable() \
                          for via_id in range(0, vn)] \
                         for net_id in range(0, nn)]

        # 各節点に対して隣接する枝の条件を作る．
        for node in graph.node_list :
            self.__make_edge_constraint(node, no_slack, use_uvar)

        # 枝が選択された時にその両端のノードのラベルが等しくなるという制約を作る．
        for edge in graph.edge_list :
            self.__make_adj_nodes_constraint(edge)

        # 各ビアについてただ1つの線分が割り当てられるという制約を作る．
        for via_id in range(0, graph.via_num) :
            self.__make_via_net_constraint(via_id)

        # 各線分についてただ一つのビアが割り当てられるという制約を作る．
        for net_id in range(0, nn) :
            self.__make_net_via_constraint(net_id)

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
    def make_ushape_constraint(self) :
        graph = self.__graph
        solver = self.__solver
        for edge1, edge2, edge3, edge4 in graph.square_edges :
            var1 = self.edge_var(edge1)
            var2 = self.edge_var(edge2)
            var3 = self.edge_var(edge3)
            var4 = self.edge_var(edge4)
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
        if node_10.is_block :
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
        if node_11.is_block :
            return

        edge_h4 = node_11.edge(dir1)

        solver = self.__solver
        var1 = self._edge_var(edge_v1)
        var4 = self._edge_var(edge_v2)
        if not (node_00.is_block or node_20.is_block) :
            var2 = self.edge_var(edge_h1)
            var3 = self.edge_var(edge_h2)
            solver.add_clause([~var1, ~var2, ~var3, ~var4])
        if not (node_01.is_block or node_21.is_block) :
            var2 = self.edge_var(edge_h3)
            var3 = self.edge_var(edge_h4)
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
                if node_10.is_block :
                    continue

                edge_h2 = node_10.lower_edge if d else node_10.x2_edge
                if edge_h2 == None :
                    continue
                node_20 = edge_h2.alt_node(node_10)
                if node_20.is_block :
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
                if node_11.is_block :
                    continue

                edge_h5 = node_11.lower_edge if d else node_11.x2_edge
                node_21 = edge_h5.alt_node(node_11)
                if node_21.is_block :
                    continue

                edge_h6 = node_21.lower_edge if d else node_21.x2_edge

                node_31 = edge_h6.alt_node(node_21)

                var_v1 = self._edge_var(edge_v1)
                var_v2 = self._edge_var(edge_v2)
                if not (node_00.is_block or node_30.is_block) :
                    var_h1 = self._edge_var(edge_h1)
                    var_h2 = self._edge_var(edge_h2)
                    var_h3 = self._edge_var(edge_h3)
                    solver.add_clause([~var_v1, ~var_v2, ~var_h1, ~var_h2, ~var_h3])
                if not (node_01.is_block or node_31.is_block) :
                    var_h4 = self._edge_var(edge_h4)
                    var_h5 = self._edge_var(edge_h5)
                    var_h6 = self._edge_var(edge_h6)
                    solver.add_clause([~var_v1, ~var_v2, ~var_h4, ~var_h5, ~var_h6])

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
            if node.is_block :
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
                if node.is_via :
                    return True, -1
            return False, 0

        # Y軸方向に端子があるかを調べる．
        def ycheck(graph, x0, y0, z0, dy, ry) :
            for i in range(1, ry) :
                y1 = y0 + i * dy
                node = graph.node(x0, y1, z0)
                if node.is_terminal :
                    return True, node.terminal_id
                if node.is_via :
                    return True, -1
            return False, 0

        xcheck, xnet_id = xcheck(graph, x0, y0, z0, dx, rx)
        ycheck, ynet_id = ycheck(graph, x0, y0, z0, dy, ry)
        if xcheck and ycheck and (xnet_id == -1 or ynet_id == -1 or (xnet_id == ynet_id)) :
            # X軸方向，Y軸方向ともに同じネット番号の端子がある場合は制約を付けない．
            return

        r = rx if rx < ry else ry
        for i in range(1, r) :
            x1 = x0 + i * dx
            y1 = y0 + i * dy
            node = graph.node(x1, y1, z0)
            if node.is_block :
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
            if node.is_block :
                continue
            self.__yshape_sub(node, 0, 2)
            self.__yshape_sub(node, 2, 0)

    def __yshape_sub(self, node_10, dir1, dir3) :
        solver = self.__solver

        node_11 = node_10.adj_node(dir3)
        if node_11 == None or node_11.is_block :
            return

        node_00 = node_10.adj_node(dir1)
        if node_00 == None :
            return
        node_20 = node_10.adj_node(dir1 + 1)
        if node_20 == None :
            return

        edge1 = node_00.edge(dir3)
        edge2 = node_20.edge(dir3)
        evar1 = self.edge_var(edge1)
        evar2 = self.edge_var(edge2)

        edge3 = node_10.edge(dir3 + 1)
        if edge3 is not None :
            evar3 = self.edge_var(edge3)
            solver.add_clause([~evar1, ~evar2,  evar3])

        edge4 = node_11.edge(dir3)
        if edge4 is not None :
            evar4 = self.edge_var(edge4)
            solver.add_clause([~evar1, ~evar2,  evar4])

    ## @brief 問題を解く．
    ## @return result, solution を返す．
    ##
    ## - result は 'OK', 'NG', 'Abort' の3種類
    ## - solution はナンバーリンクの解
    def solve(self, var_limit) :
        self.__time1 = time.time()
        print(' CPU time for CNF generating: {:7.2f}s'.format(self.__time1 - self.__time0))
        solver = self.__solver
        print(' # of variables: {}'.format(solver.variable_num()))
        print(' # of clauses:   {}'.format(solver.clause_num()))
        print(' # of literals:  {}'.format(solver.literal_num()))
        if var_limit > 0 and self.__solver.variable_num() > var_limit :
            print('  variable limit ({}) exceeded'.format(var_limit))
            return 'Abort', None
        stat, model = solver.solve()
        self.__time2 = time.time()
        print(' CPU time for SAT solving:    {:7.2f}s'.format(self.__time2 - self.__time1))
        if stat == Bool3.TRUE :
            print('OK')
            verbose = False
            net_num = self.__graph.net_num
            route_list = [self.__find_route(net_id, model) for net_id in range(0, net_num)]
            router = Router(self.__graph.dimension, route_list, verbose)
            router.reroute()
            solution = router.to_solution()
            return 'OK', solution
        elif stat == Bool3.FALSE :
            print('NG')
            return 'NG', None
        elif stat == Bool3.UNKNOWN :
            print('Abort')
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
                elit = self.edge_var(edge)
                evar = elit.varid()
                if model[evar.val()] != Bool3.TRUE :
                    continue
                node1 = edge.alt_node(node)
                if node1 == prev :
                    continue
                next = node1
                break
            if next == None :
                # このノードがビアなら end の層まで移動する．
                assert node.is_via
                assert start.z != end.z
                x0 = node.x
                y0 = node.y
                if start.z < end.z :
                    for z in range(start.z, end.z) :
                        route.append(Point(x0, y0, z))
                else :
                    for z in range(start.z, end.z, -1) :
                        route.append(Point(x0, y0, z))
                next = graph.node(node.x, node.y, end.z)
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
    ### - ビアの場合
    ###   nv_map の変数によって終端になる場合と孤立する場合がある．
    ### - それ以外
    ###   全て選ばれないか2つの枝が選ばれる．
    def __make_edge_constraint(self, node, no_slack, use_uvar) :
        solver = self.__solver
        graph = self.__graph

        # node に接続している枝の変数のリスト
        evar_list = [self.edge_var(edge) for edge in node.edge_list]

        if node.is_terminal :
            # node が終端の場合

            # ただ一つの枝が選ばれる．
            solver.add_exact_one(evar_list)

            # 同時にラベルの変数を固定する．
            net_id = node.terminal_id
            label = graph.label(net_id, node.z)
            assert label != -1
            self.__make_label_constraint(node, label)
        elif node.is_via :
            # node がビアの場合
            # この層に終端を持つ線分と結びついている時はただ一つの枝が選ばれる．
            via_id = node.via_id
            for net_id in graph.via_net_list(via_id) :
                label = graph.label(net_id, node.z)
                if label == -1 :
                    continue
                cvar = self.__nv_map[net_id][via_id]
                solver.set_conditional_literals([cvar])
                node1, node2 = graph.terminal_node_pair(net_id)
                if node1.z != node.z and node2.z != node.z :
                    # このビアは net_id の線分には使えない．
                    # このノードに接続する枝は選ばれない．
                    for evar in evar_list :
                        solver.add_clause([~evar])
                else :
                    # このビアを終端と同様に扱う．
                    solver.add_exact_one(evar_list)

                    # ラベルの制約を追加する．
                    self.__make_label_constraint(node, label)
                solver.clear_conditional_literals()
        else :
            if no_slack :
                # 常に２個の枝が選ばれる．
                solver.add_exact_two(evar_list)
            elif self.__use_uvar :
                uvar = self.__uvar_list[node.id]
                solver.add_at_most_two(evar_list)
                solver.add_at_least_two(evar_list, cvar_list = [uvar])
                solver.set_conditional_literals([~uvar])
                for evar in evar_list :
                    solver.add_clause([~evar])
                solver.clear_conditional_literals()
            else :
                # ０個か２個の枝が選ばれる．
                solver.add_at_most_two(evar_list)
                solver.add_not_one(evar_list)

    ### @brief via_id に関してただ一つの線分が選ばれるという制約を作る．
    def __make_via_net_constraint(self, via_id) :
        graph = self.__graph

        # このビアに関係するネットを調べ，対応するビア割り当て変数のリストを作る．
        vars_list = [self.__nv_map[net_id][via_id] for net_id in graph.via_net_list(via_id)]

        # この変数に対する one-hot 制約を作る．
        solver = self.__solver
        solver.add_exact_one(vars_list)

    ### @brief net_id に関してただ一つのビアが選ばれるという制約を作る．
    def __make_net_via_constraint(self, net_id) :
        graph = self.__graph
        # このネットに関係のあるビアを調べ，対応するビア割り当て変数のリストを作る．
        vars_list = [self.__nv_map[net_id][via_id] for via_id in graph.net_via_list(net_id)]

        # この変数に対する one-hot 制約を作る．
        solver = self.__solver
        solver.add_exact_one(vars_list)

    ### @brief 枝の両端のノードのラベルに関する制約を作る．
    ### @param[in] edge 対象の枝
    ###
    ### 具体的にはその枝が選ばれているとき両端のノードのラベルは等しい
    def __make_adj_nodes_constraint(self, edge) :
        solver = self.__solver
        evar = self.edge_var(edge)
        solver.set_conditional_literals([evar])
        nvar_list1 = self.__node_vars_list[edge.node1.id]
        nvar_list2 = self.__node_vars_list[edge.node2.id]
        n = len(nvar_list1)
        for i in range(0, n) :
            nvar1 = nvar_list1[i]
            nvar2 = nvar_list2[i]
            solver.add_eq_rel(nvar1, nvar2)
        solver.clear_conditional_literals()
        if self.__binary_encoding :
            pass
        else :
            solver.set_conditional_literals([~evar])
            for i in range(0, n) :
                var1 = nvar_list1[i]
                var2 = nvar_list2[i]
                solver.add_clause([~var1, ~var2])
            solver.clear_conditional_literals()

    ## @brief ラベル値を固定する制約を作る．
    # @param[in] node 対象のノード
    # @param[in] net_id 固定する線分番号
    def __make_label_constraint(self, node, net_id) :
        solver = self.__solver
        lvar_list = self.__node_vars_list[node.id]
        if self.__binary_encoding :
            for i, lvar in enumerate(lvar_list) :
                if (1 << i) & (net_id + 1) :
                    solver.add_clause([lvar])
                else :
                    solver.add_clause([~lvar])
        else :
            for i, lvar in enumerate(lvar_list) :
                if i == net_id :
                    solver.add_clause([lvar])
                else :
                    solver.add_clause([~lvar])

    ## @brief ノードに対する uvar を返す．
    def node_uvar(self, node) :
        return self.__uvar_list[node.id]

    ## @brief 枝に対する変数番号を返す．
    # @param[in] edge 対象の枝
    def edge_var(self, edge) :
        return self.__edge_var_list[edge.id]

# end-of-class NlCnfEncoder
