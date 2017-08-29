#! /usr/bin/env python3
#
# @file nlsolution.py
# @brief NlSolution の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlgraph import NlNode, NlGraph

## @brief 解を表すクラス
#
class NlSolution :

    ## @brief 初期化
    def __init__(self) :
        self.__width = 0
        self.__height = 0
        self.__depth = 0
        self.__grid_array = []

    ## @brief グラフと経路リストから内容を設定する．
    # @param[in] graph 問題を表すグラフ
    # @param[in] route_list 各線分の経路のリスト
    #
    # 経路は NlNode のリスト
    def set_from_routes(self, graph, route_list) :
        self.set_size(graph.width, graph.height, graph.depth)

        # 経路上のマス目に線分番号を書き込む．
        for net_id in range(0, graph.net_num) :
            route = route_list[net_id]
            for node in route :
                x = node.x
                y = node.y
                z = node.z
                self.__grid_array[x][y][z] = net_id + 1

    ## @brief サイズを設定する．
    # @param[in] width 幅
    # @param[in] height 高さ
    # @param[in] depth 層数
    def set_size(self, width, height, depth) :
        self.__width = width
        self.__height = height
        self.__depth = depth

        # 各マス目の線分番号を格納する３次元配列を作る．
        # 値は 0 に初期化される．
        self.__grid_array = [[[0 for z in range(0, self.__depth)]\
                              for y in range(0, self.__height)]\
                             for x in range(0, self.__width)]

    ## @brief マス目の値を設定する．
    # @param[in] x, y, z 座標
    # @param[in] val 値
    def set_val(self, x, y, z, val) :
        assert 0 <= x < self.__width
        assert 0 <= y < self.__height
        assert 0 <= z < self.__depth
        self.__grid_array[x][y][z] = val

    ## @brief 値を得る．
    def val(self, x, y, z) :
        return self.__grid_array[x][y][z]

    ## @brief 内容を出力する．
    # @param[in] fout 出力先のファイルオブジェクト
    def print(self, fout) :
        print('SIZE {}X{}X{}'.format(self.__width, self.__height, self.__depth), file=fout)
        for z in range(0, self.__depth) :
            print('LAYER {}'.format(z + 1), file=fout)
            for y in range(0, self.__height) :
                line = ''
                comma = ''
                for x in range(0, self.__width) :
                    line += comma
                    comma = ','
                    line += '{:02d}'.format(self.__grid_array[x][y][z])
                print(line, file=fout)
