#! /usr/bin/env python3

### @file dimension.py
### @brief Dimension の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

from nl3d.point import Point


### @brief 問題のサイズを表すクラス
###
### 基本的に初期化時に設定した値は変更されない．
class Dimension :

    ### @brief 初期化
    ### @param[in] width 幅
    ### @param[in] height 高さ
    ### @param[in] depth 層数
    def __init__(self, width, height, depth) :
        self.__width = width
        self.__height = height
        self.__depth = depth

    ### @brief 幅(X軸方向のサイズ)
    @property
    def width(self) :
        return self.__width

    ### @brief 高さ(Y軸方向のサイズ)
    @property
    def height(self) :
        return self.__height

    ### @brief 深さ(Z軸方向のサイズ)
    @property
    def depth(self) :
        return self.__depth

    ### @brief 全グリッドサイズ
    ###
    ### = width * height * depth
    @property
    def grid_size(self) :
        return self.__width * self.__height * self.__depth

    ### @brief 座標をインデックスに変換する．
    ### @param[in] x, y, z 座標
    ### @return インデックスを返す．
    ### @sa index_to_point
    def xyz_to_index(self, x, y, z) :
        assert self.range_check(x, y, z)
        return ((z * self.__height) + y) * self.__width + x

    ### @brief Pointをインデックスに変換する．
    ### @param[in] point 位置(Point)
    ### @return インデックスを返す．
    ### @sa index_to_point
    def point_to_index(self, point) :
        x, y, z = point.xyz
        return self.xyz_to_index(x, y, z)

    ### @brief インデックスを座標に変換する．
    ### @param[in] index インデックス
    ### @return 座標(x, y, zのタプル)を返す．
    def index_to_xyz(self, index) :
        x = index % self.__width
        index //= self.__width
        y = index % self.__height
        index //= self.__height
        z = index
        return x, y, z

    ### @brief インデックスを位置(Point)に変換する．
    ### @param[in] index インデックス
    ### @return 位置(Point)を返す．
    def index_to_point(self, index) :
        x, y, z = self.index_to_xyz(index)
        return Point(x, y, z)

    ### @brief 座標が範囲内にあるかチェックする．
    ### @param[in] x, y, z 座標
    ### @retval True 座標が範囲内だった．
    ### @retval False 座標が範囲外だった．
    def range_check(self, x, y, z) :
        if x < 0 or x >= self.__width :
            return False
        if y < 0 or y >= self.__height :
            return False
        if z < 0 or z >= self.__depth :
            return False
        return True

    ### @brief 位置(Point)が範囲内にあるかチェックする．
    ### @param[in] point 位置
    ### @retval True 座標が範囲内だった．
    ### @retval False 座標が範囲外だった．
    def point_check(self, point) :
        return self.range_check(point.x, point.y, point.z)

# end of dimension.py
