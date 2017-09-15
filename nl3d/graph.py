#! /usr/bin/env python3

### @file graph.py
### @brief Graph の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.


### @brief 節点を表すクラス
###
### 以下のメンバを持つ．
### - ID番号
### - 位置(__point)
### - 接続している枝のリスト(__edge_list)
### - 各方向の枝(__x1_edge, __x2_edge, __y1_edge, __y2_edge, __z1__edge, __z2_edge)
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
        self.__z1_edge = None
        self.__z2_edge = None
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
        ans = '#{:04d}: {}'.format(self.id, self.point)

        if self.is_terminal :
            ans += ' [Net#{}]'.format(self.terminal_id)

        if self.is_via :
            ans += ' [Via#{}]'.format(self.via_id)

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


### @brief デフォルトの形式を推定する．
def guess_format(problem) :
    if problem.depth == 1 :
        return 'adc2015'
    if problem.via_num > 0 :
        return 'adc2016'
    return 'adc2017'

### @brief ナンバーリンクの問題を表すグラフ
###
### ADC2015, ADC2016, ADC207 共用
### * ADC2015 は単層なので Z 軸方向の枝がない．
### * ADC2016 は多層だがビアを持つので Z軸方向の枝がない．
### * ADC2017 は多層でかつZ軸方向の枝を持つ．
###
### ちなみに単相の問題は全てのバージョンで同一となる．
### 問題は ADC2016 でビアのない多層問題．
### これは独立した複数枚の問題を寄せ集めただけなのだが，ADC2017 では
### すべてが繋がった多層問題となるが，問題ファイルを見ただけでは区別ができない．
### このときだけ形式を指定する必要がある．
class Graph :

    ### @brief 初期化
    ### @param[in] problem 問題を表すオブジェクト(Problem)
    ### @param[in] format 問題の形式('adc2015', 'adc2016', 'adc2017')
    def __init__(self, problem, format = None) :
        self.set_problem(problem, format)

    ### @brief 問題を設定する．
    ### @param[in] problem 問題を表すオブジェクト(Problem)
    ### @param[in] format 問題の形式('adc2015', 'adc2016', 'adc2017')
    def set_problem(self, problem, format = None) :
        if format :
            assert format == 'adc2015' or format == 'adc2016' or format == 'adc2017'
        dimension = problem.dimension
        self.__dim = dimension
        self.__net_num = problem.net_num
        self.__via_num = problem.via_num
        self.__has_via = True if self.__via_num > 0 else False

        if format is None :
            format = guess_format(problem)
        elif (dimension.depth > 1 and format == 'adc2015') or \
               (problem.via_num > 0 and format == 'adc2017') :
            format = guess_format(problem)
            print('Graph.set_problem(): format error: {} is assumed.'.format(format))
        self.__format = format

        # 節点を作る．
        # node_array[index] に (x, y, z) の節点が入る．
        # ただし index = dimension.xyz_to_index(x, y, z)
        # Python 特有の内包表記で one-liner で書けるけど1行が長すぎ．
        self.__node_array = [self.__new_node(index) for index in range(0, dimension.grid_size)]

        # 枝を作る．
        self.__edge_list = []
        for z in range(0, self.depth) :
            # x方向の枝を作る．
            for x in range(0, self.width - 1) :
                for y in range(0, self.height) :
                    # (x, y, z) - (x + 1, y, z) を結ぶ枝
                    node1 = self.node(x    , y, z)
                    node2 = self.node(x + 1, y, z)
                    self.__new_edge(node1, node2, 0)

            # y方向の枝を作る．
            for x in range(0, self.width) :
                for y in range(0, self.height - 1) :
                    # (x, y, z) - (x, y + 1, z) を結ぶ枝
                    node1 = self.node(x, y    , z)
                    node2 = self.node(x, y + 1, z)
                    self.__new_edge(node1, node2, 1)

        if format == 'adc2017' :
            # z 方向の枝を作る．
            for x in range(0, self.width) :
                for y in range(0, self.height) :
                    for z in range(0, self.depth - 1) :
                        # (x, y, z) - (x, y, z + 1) を結ぶ枝
                        node1 = self.node(x, y, z    )
                        node2 = self.node(x, y, z + 1)
                        self.__new_edge(node1, node2, 2)

        # 端子の印をつける．
        self.__terminal_node_pair_list = []
        for net_id, (label, s, e) in enumerate(problem.net_list()) :
            node1 = self.node(s.x, s.y, s.z)
            node2 = self.node(e.x, e.y, e.z)
            node1.set_terminal(net_id)
            node2.set_terminal(net_id)
            self.__terminal_node_pair_list.append((node1, node2))

        if format == 'adc2016' :
            # 各層ごとに現れるネット番号のリストを作る．
            self.__terminal_node_pair_list = []
            self.__multi_net_list = []
            self.__multi_net_id_map = [-1 for (label, s, e) in problem.net_list()]
            self.__net_id_list = [[] for z in range(0, self.depth)]
            for net_id, (label, s, e) in enumerate(problem.net_list()) :
                node1 = self.node(s.x, s.y, s.z)
                node2 = self.node(e.x, e.y, e.z)
                node1.set_terminal(net_id)
                node2.set_terminal(net_id)
                self.__terminal_node_pair_list.append((node1, node2))
                self.__net_id_list[s.z].append(net_id)
                if s.z != e.z :
                    multi_net_id = len(self.__multi_net_list)
                    self.__multi_net_id_map[net_id] = multi_net_id
                    self.__multi_net_list.append(net_id)
                    self.__net_id_list[e.z].append(net_id)

            # __net_id_list の最大値がラベル数となる．
            max_num = 0
            for z in range(0, self.depth) :
                num = len(self.__net_id_list[z])
                if max_num < num :
                    max_num = num
            self.__label_num = max_num

            # (ネット番号, 層番号)とラベルの対応付けを行う．
            self.__label_matrix = [[-1 for z in range(0, self.depth)] for d in range(0, self.net_num)]
            for z in range(0, self.depth) :
                for label, net_id in enumerate(self.__net_id_list[z]) :
                    self.__label_matrix[net_id][z] = label

            # ビアの印をつける．
            self.__via_nodes_list = [[] for via_id in range(0, self.via_num)]
            for via_id, via in enumerate(problem.via_list()) :
                via_nodes = []
                for z in range(via.z1, via.z2 - via.z1 + 1) :
                    node = self.node(via.x, via.y, z)
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

    ### @brief 問題の形式
    @property
    def format(self) :
        return self.__format

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

    ### @brief ビア数
    @property
    def via_num(self) :
        return self.__via_num

    ### @brief ビアを持っている時に True を返す．
    @property
    def has_via(self) :
        return self.__has_via

    ### @brief ノードのリスト
    @property
    def node_list(self) :
        return self.__node_array

    ### @brief 枝のリスト
    @property
    def edge_list(self) :
        return self.__edge_list

    ### @brief 端点のノード対を返す．
    ### @param[in] net_id 線分番号
    def terminal_node_pair(self, net_id) :
        return self.__terminal_node_pair_list[net_id]

    ### @brief 多層ネット数
    @property
    def multi_net_num(self) :
        return len(self.__multi_net_list)

    ### @brief 多層ネットのネット番号のリスト
    @property
    def multi_net_list(self) :
        return self.__multi_net_list

    ### @brief 線分番号から多層ネット番号を得る．
    ### @param[in] net_id 線分番号
    ###
    ### net_id が多層ネットでない場合には -1 を返す．
    def multi_net_id(self, net_id) :
        return self.__multi_net_id_map[net_id]

    ### @brief 線分番号を表すラベル数
    ###
    ### 基本的には線分数と同じだが，互いに独立な層にある線分には
    ### 同じラベルを割り振ることができるので場合によっては少なくなる．
    @property
    def label_num(self) :
        return self.__label_num

    ### @brief 線分番号に対するラベルを返す．
    ### @param[in] net_id 線分番号
    ### @param[in] z 層番号
    ###
    ### その層にない線分番号の場合には -1 を返す．
    def label(self, net_id, z) :
        return self.__label_matrix[net_id][z]

    ### @brief ネットに関係するビア番号のリストを返す．
    ### @param[in] net_id 線分番号
    ###
    ### has_via == True の時のみ意味を持つ．
    def net_via_list(self, net_id) :
        return self.__net_via_list[net_id]

    ### @brief ビアのノードリストを返す．
    ### @param[in] via_id ビア番号
    ###
    ### has_via == True の時のみ意味を持つ．
    def via_node_list(self, via_id) :
        return self.__via_nodes_list[via_id]

    ### @brief ビアに関係する線分番号のリストを返す．
    ### @param[in] via_id ビア番号
    ###
    ### has_via == True の時のみ意味を持つ．
    def via_net_list(self, via_id) :
        return self.__via_net_list[via_id]

    ### @brief 多層ネット番号とビアの候補対のリスト
    @property
    def via_net_pair_list(self) :
        return self.__via_net_pair_list

    ### @brief 座標を指定して対応するノードを返す．
    ### @param[in] x, y, z 座標
    def node(self, x, y, z) :
        index = self.__dim.xyz_to_index(x, y, z)
        return self.__node_array[index]

    ### @brief 位置(Point) から対応するノードを返す．
    ### @param[in] point 位置(Point)
    def node_from_point(self, point) :
        index = self.__dim.point_to_index(point)
        return self.__node_array[index]

    ### @brief ロの字を形作る４組の枝を列挙する．
    ###
    ### node_00 -- edge1 -- node_10
    ###    |                   |
    ###    |                   |
    ###  edge2               edge3
    ###    |                   |
    ###    |                   |
    ### node_01 -- edge4 -- node_11
    ###
    ### このような位置関係にある edge1, edge2, edge3, edge4 を
    ### 列挙するジェネレータを返す．
    @property
    def square_edges(self) :
        dir1 = 1
        dir2 = 3
        for node_00 in self.__node_array :
            edge1 = node_00.edge(dir1)
            if edge1 == None :
                continue
            edge2 = node_00.edge(dir2)
            if edge2 == None :
                continue
            node_10 = edge1.alt_node(node_00)
            assert node_10 != None
            node_01 = edge2.alt_node(node_00)
            assert node_01 != None
            edge3 = node_10.edge(dir2)
            assert edge3 != None
            edge4 = node_01.edge(dir1)
            assert edge4 != None
            yield edge1, edge2, edge3, edge4

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
    ### @param[in] index インデックス番号
    def __new_node(self, index) :
        point = self.__dim.index_to_point(index)
        return Node(index, point)

    ### @brief 内容を出力する．
    def dump(self) :
        print('Nodes:')
        for node in self.__node_array :
            node.dump()

        print('')
        print('Edges:')
        for edge in self.__edge_list :
            edge.dump()

# end of graph.py
