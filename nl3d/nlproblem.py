#! /usr/bin/env python3

## @file nlproblem.py
# @brief NlProblem の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlpoint import NlPoint
from nl3d.nlvia import NlVia

## @brief 問題を表すクラス
#
# 内部で保持している情報は以下の通り
# - 幅
# - 高さ
# - 層数
# - ネットの端点のリスト
# - ビアのリスト
#
# 値を設定する時はまず set_size(w, h, d) でサイズを設定し，
# そのあとで add_net(label, start, end) でネットを追加し，
# add_via(label, x, y, z1, z2) でビアを追加する．
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
#
# 同様にビアは via_list() で取得できる．
#
# @code
# for via_id, v in problem.via_list() :
#   # via_id はビア番号
#   # v は NlVia のオブジェクトとなっている．
#   pass
# @endcode
#
# という風に使うことを想定している．<br>
# ビア番号はリスト中のインデックス<br>
# これはビアのラベルとは無関係<br>
# ビアはラベルをキーにして取得することもできる．
#
# @code
# if problem.has_via(label) :
#     via = problem.via(label)
#     ...
# @endcode
#
# という風に使う．
class NlProblem :

    ## @brief 初期化
    def __init__(self) :
        self.clear()


    ## @brief クリアする．
    def clear(self) :
        self._width = 0
        self._height = 0
        self._depth = 0
        self._net_list = []
        self._net_dict = {}
        self._via_list = []
        self._via_dict = {}


    ## @brief サイズを設定する．
    # @param[in] width 幅
    # @param[in] height 高さ
    # @param[in] depth 層数
    def set_size(self, width, height, depth) :
        self.clear()

        self._width = width
        self._height = height
        self._depth = depth


    ## @brief 線分を追加する．
    # @param[in] label ラベル
    # @param[in] start_point 始点の座標
    # @param[in] end_point 終点の座標
    #
    # 始点と終点の順番に意味はない．入れ替わっても同じ問題を表す．
    def add_net(self, label, start_point, end_point) :

        if label in self._net_dict :
            # すでに label というラベルのネットがあった．
            # スキップするだけ．
            print('Error: Net#{} already exists.'.format(label))
            return

        self._net_list.append( (label, start_point, end_point) )
        self._net_dict[label] = (start_point, end_point)


    ## @brief ビアを追加する．
    # @param[in] label ラベル
    # @param[in] x X座標
    # @param[in] y Y座標
    # @param[in] z1 Z座標(層番号)の下限
    # @param[in] z2 Z座標(層番号)の上限
    #
    # z1 < z2 を仮定している．
    def add_via(self, label, x, y, z1, z2) :
        assert z1 < z2

        if label in self._via_dict :
            # すでに label というラベルのビアがあった．
            # スキップするだけ．
            print('Error: Via#{} already exists.'.format(label))
            return

        via = NlVia(label, x, y, z1, z2)
        self._via_list.append(via)
        self._via_dict[label] = via


    ## @brief 幅を返す．
    @property
    def width(self) :
        return self._width


    ## @brief 高さを返す．
    @property
    def height(self) :
        return self._height


    ## @brief 層数を返す．
    @property
    def depth(self) :
        return self._depth

    ## @brief 線分数を返す．
    @property
    def net_num(self) :
        return len(self._net_list)

    ## @brief ビア数を返す．
    @property
    def via_num(self) :
        return len(self._via_list)

    ## @brief 線分を返す．
    #
    # これは for 文で使われることを想定している．
    def net_list(self) :
        for label, start_point, end_point in self._net_list :
            yield label, start_point, end_point


    ## @brief label というラベルを持つネットがあるか調べる．
    def has_net(self, label) :
        return label in self._net_dict


    ## @brief label というラベルを持つネットを返す．
    # @return (start, end) というタプルを返す．
    #
    # なければ None を返す．
    def net(self, label) :
        if label in self._net_dict :
            return self._net_dict[label]
        else :
            return None


    ## @brief ビアを返す．
    #
    # これは for 文で使われることを想定している．
    def via_list(self) :
        for via in self._via_list :
            yield via


    ## @brief label というラベルを持つビアがあるか調べる．
    def has_via(self, label) :
        return label in self._via_dict


    ## @brief label というラベルを持つビアを返す．
    #
    # なければ None を返す．
    def via(self, label) :
        if label in self._via_dict :
            return _via_dict[label]
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

        for via_id, via in enumerate(self.via_list()) :
            print('[{:2d}] Via#{}: {}, {}, {} - {}'.format(via_id, via.label, via.x, via.y, via.z1, via.z2))
