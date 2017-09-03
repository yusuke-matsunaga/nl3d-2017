#! /usr/bin/env python3
#
## @file nlpoint.py
# @brief nlpoint の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

## @brief 座標を表すクラス
#
# 単純に (x, y, z) の３次元の座標を持つ．
#
# @code
# p1 = NlPoint(1, 2, 3)
# x1 = p1.x
# y1 = p1.y
# z1 = p1.z
# @endcode
#
# という風に使う．
class NlPoint :

    ## @brief 初期化
    # @param x, y, z 座標の値
    def __init__(self, x = 0, y = 0, z = 0) :
        self.__x = x
        self.__y = y
        self.__z = z

    ## @brief X座標を得る．
    @property
    def x(self) :
        return self.__x

    ## @brief Y座標を得る．
    @property
    def y(self) :
        return self.__y

    ## @brief Z座標を得る．
    @property
    def z(self) :
        return self.__z
