#! /usr/bin/env python3

### @file nlsolution.py
### @brief Solution の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import sys

### @brief 解を表すクラス
class Solution :

    ### @brief 初期化
    def __init__(self) :
        self.__dim = None
        self.__grid_array = []

    ### @brief サイズを設定する．
    ### @param[in] dim サイズ(Dimension)
    def set_size(self, dim) :
        self.__dim = dim

        # 各マス目の線分番号を格納する配列を作る．
        # 配列のインデックスは Dimension で計算する．
        # 値は 0 に初期化される．
        self.__grid_array = [0 for i in range(0, self.__dim.grid_size)]

    ### @brief グラフと経路リストから内容を設定する．
    ### @param[in] dim サイズ(Dimension)
    ### @param[in] route_list 各線分の経路のリスト
    ###
    ### 経路は Point のリスト
    def set_from_route_list(self, dim, route_list) :
        self.set_size(dim)

        # 経路上のマス目に線分番号を書き込む．
        for net_id, route in enumerate(route_list) :
            val = net_id + 1
            for node in route :
                set_val(node.point, val)

    ### @brief マス目の値を設定する．
    ### @param[in] point 位置
    ### @param[in] val 値
    def set_val(self, point, val) :
        assert self.__dim.point_check(point)
        index = self.__dim.point_to_index(point)
        self.__grid_array[index] = val

    ### @brief サイズ(Dimension)
    @property
    def dimension(self) :
        return self.__dim

    ### @brief 幅(X軸方向のサイズ)
    @property
    def width(self) :
        return self.__dim.width

    ### @brief 高さ(Y軸方向のサイズ)
    @property
    def height(self) :
        return self.__dim.height

    ### @brief 層数(Z軸方向のサイズ)
    @property
    def depth(self) :
        return self.__dim.depth

    ### @brief 値を得る．
    ### @param[in] point 位置
    def val(self, point) :
        index = self.__dim.point_to_index(point)
        return self.__grid_array[index]

    ### @brief 内容を出力する．
    ### @param[in] fout 出力先のファイルオブジェクト
    ###
    ### fout が省略された場合には標準出力が用いられる．
    def print(self, fout = sys.stdout) :
        print('SIZE {}X{}X{}'.format(self.width, self.height, self.depth), file = fout)
        for z in range(0, self.depth) :
            print('LAYER {}'.format(z + 1), file = fout)
            for y in range(0, self.height) :
                line = ''
                comma = ''
                for x in range(0, self.width) :
                    line += comma
                    comma = ','
                    index = self.__dim.xyz_to_index(x, y, z)
                    line += '{:3d}'.format(self.__grid_array[index])
                print(line, file=fout)

# end of solution.py
