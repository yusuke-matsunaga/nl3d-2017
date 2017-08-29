#! /usr/bin/env python3

## @file nlproblem.py
# @brief NlProblem の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlpoint import NlPoint

## @brief 問題を表すクラス
#
# 内部で保持している情報は以下の通り
# - 幅
# - 高さ
# - 層数
# - ネットの端点のリスト
#
# 値を設定する時はまず set_size(w, h, d) でサイズを設定し，
# そのあとで add_net(label, start, end) でネットを追加する．
# 設定された内容は clear() を呼ぶまで変わらない．
#
# ネットは net_list() で取得できる．これは反復子になっているので
#
# @code
# for net_id, label, start_point, end_point in problem.net_list() :
#   # net_id にネット番号(int)
#   # label にラベル(int というか任意)
#   # start_point に始点の座標(NlPoint)
#   # end_point に終点の座標(NlPoint)
#   # が入る
#   ...
# @endcode
#
# という風に使うことを想定している．<br>
# ネット番号はリスト中のインデックス．<br>
# ちなみにネットの始点と終点の順番に意味はない．<br>
class NlProblem :

    ## @brief 初期化
    def __init__(self) :
        self.clear()

    ## @brief クリアする．
    def clear(self) :
        self.__width = 0
        self.__height = 0
        self.__depth = 0
        self.__net_list = []
        self.__net_dict = {}

    ## @brief サイズを設定する．
    # @param[in] width 幅
    # @param[in] height 高さ
    # @param[in] depth 層数
    def set_size(self, width, height, depth) :
        self.clear()

        self.__width = width
        self.__height = height
        self.__depth = depth

    ## @brief 線分を追加する．
    # @param[in] label ラベル
    # @param[in] start_point 始点の座標
    # @param[in] end_point 終点の座標
    #
    # 始点と終点の順番に意味はない．入れ替わっても同じ問題を表す．
    def add_net(self, label, start_point, end_point) :

        if label in self.__net_dict :
            # すでに label というラベルのネットがあった．
            # スキップするだけ．
            print('Error: Net#{} already exists.'.format(label))
            return

        self.__net_list.append( (label, start_point, end_point) )
        self.__net_dict[label] = (start_point, end_point)

    ## @brief 幅を返す．
    @property
    def width(self) :
        return self.__width

    ## @brief 高さを返す．
    @property
    def height(self) :
        return self.__height

    ## @brief 層数を返す．
    @property
    def depth(self) :
        return self.__depth

    ## @brief 線分数を返す．
    @property
    def net_num(self) :
        return len(self.__net_list)

    ## @brief 線分を返す．
    #
    # これは for 文で使われることを想定している．
    def net_list(self) :
        for label, start_point, end_point in self.__net_list :
            yield label, start_point, end_point

    ## @brief label というラベルを持つネットがあるか調べる．
    def has_net(self, label) :
        return label in self.__net_dict

    ## @brief label というラベルを持つネットを返す．
    # @return (start, end) というタプルを返す．
    #
    # なければ None を返す．
    def net(self, label) :
        if label in self.__net_dict :
            return self.__net_dict[label]
        else :
            return None

    ## @brief 内容を書き出す．
    #
    # 主にデバッグ用
    def dump(self) :
        print('width  = {}'.format(self.width))
        print('height = {}'.format(self.height))
        print('depth  = {}'.format(self.depth))

        for net_id, (label, start_point, end_point) in enumerate(self.net_list()) :
            print('[{:2d}] Net#{}: ({}, {}, {}) - ({}, {}, {})'.format(net_id, label, start_point.x, start_point.y, start_point.z, end_point.x, end_point.y, end_point.z))
