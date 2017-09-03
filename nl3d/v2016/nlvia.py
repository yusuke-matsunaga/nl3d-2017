#! /usr/bin/env python3

## @file nlvia.py
# @brief NlVia の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

## @brief ビアを表すクラス
#
# ラベル(文字列)とビアのある x, y 軸上の座標と z 軸(層)の範囲(上限, 下限)を持つ．
#
# @code
# # (1, 2) の位置に3層と4層を結ぶ'a'というラベルのビアを作る．
# v1 = NlVia('a', 1, 2, 3, 4)
# l = v1.label  # l は 'a'
# x = v1.x      # x1 は1
# y = v1.y      # y1 は2
# z_l = v1.z1   # z_l は3
# z_u = v1.z2   # z_u は4
# @endcode
#
# という風に使う．
class NlVia :

    ## @brief 初期化
    # @param[in] label ラベル
    # @param[in] x X座標
    # @param[in] y Y座標
    # @param[in] z1 Z座標(層番号)の下限
    # @param[in] z2 Z座標(層番号)の上限
    #
    # z1 <= z2 を仮定している．
    def __init__(self, label = '', x = 0, y = 0, z1 = 0, z2 = 0) :
        self._label = label
        self._x = x
        self._y = y
        self._z1 = z1
        self._z2 = z2


    ## @brief ラベルを得る．
    @property
    def label(self) :
        return self._label


    ## @brief X座標を得る．
    @property
    def x(self) :
        return self._x


    ## @brief Y座標を得る．
    @property
    def y(self) :
        return self._y


    ## @brief 最下層のZ座標を得る．
    @property
    def z1(self) :
        return self._z1


    ## @brief 最上層のZ座標を得る．
    @property
    def z2(self) :
        return self._z2
