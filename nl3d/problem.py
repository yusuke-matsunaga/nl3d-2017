#! /usr/bin/env python3

### @file problem.py
### @brief Problem の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.


### @brief 問題を表すクラス
###
### 内部で保持している情報は以下の通り
### - 幅
### - 高さ
### - 層数
### - ネットの端点のリスト
### - ビアのリスト
###
### ちなみにビア情報を持つのは ADC2016 フォーマットのみ<br>
###
### 値を設定する時はまず set_size(w, h, d) でサイズを設定し，
### そのあとでネットは add_net(label, start, end) で追加する．
### ビアは add_via(via) で追加する．
### 設定された内容は clear() を呼ぶまで変わらない．
###
### ネットは net_list() で取得できる．これは反復子になっているので
###
### @code
### for label, start_point, end_point in problem.net_list() :
###   # label にラベル(int というか任意)
###   # start_point に始点の座標(Point)
###   # end_point に終点の座標(Point)
###   # が入る
###   ...
### @endcode
###
### という風に使うことを想定している．<br>
### ネット番号はリスト中のインデックス．<br>
### ちなみにネットの始点と終点の順番に意味はない．<br>
###
### 同様にビアは via_list() で取得できる．
###
### @code
### for via in problem.via_list() :
###   # via は Via のオブジェクトとなっている．
###   ...
### @endcode
###
### という風に使うことを想定している．<br>
### ビア番号はリスト中のインデックス<br>
### これはビアのラベルとは無関係<br>
### ビアはラベルをキーにして取得することもできる．
###
### @code
### if problem.has_via(label) :
###     via = problem.via(label)
###     ...
### @endcode
###
### という風に使う．
class Problem :

    ### @brief 初期化
    ###
    ### サイズは未定．set_size() を呼ぶまで他の関数は使えない．
    def __init__(self) :
        self.clear()

    ### @brief クリアする．
    def clear(self) :
        self.__dim = None
        self.__net_list = []
        self.__net_dict = {}
        self.__via_list = []
        self.__via_dict = {}

    ### @brief サイズを設定する．
    ### @param[in] dim サイズ
    def set_size(self, dim) :
        self.clear()
        self.__dim = dim

    ### @brief 線分を追加する．
    ### @param[in] label ラベル
    ### @param[in] start_point 始点の座標
    ### @param[in] end_point 終点の座標
    ###
    ### 始点と終点の順番に意味はない．入れ替わっても同じ問題を表す．
    def add_net(self, label, start_point, end_point) :

        if label in self.__net_dict :
            # すでに label というラベルのネットがあった．
            # スキップするだけ．
            print('Error: Net#{} already exists.'.format(label))
            return

        self.__net_list.append( (label, start_point, end_point) )
        self.__net_dict[label] = (start_point, end_point)

    ### @brief ビアを追加する．
    ### @param[in] label ラベル
    ### @param[in] x X座標
    ### @param[in] y Y座標
    ### @param[in] z1 Z座標(層番号)の下限
    ### @param[in] z2 Z座標(層番号)の上限
    ###
    ### z1 < z2 を仮定している．
    def add_via(self, via) :
        if via.label in self.__via_dict :
            # すでに via.label というラベルのビアがあった．
            # スキップするだけ．
            print('Error: Via#{} already exists.'.format(via.label))
            return

        self.__via_list.append(via)
        self.__via_dict[via.label] = via

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

    ### @brief 線分数．
    @property
    def net_num(self) :
        return len(self.__net_list)

    ### @brief 線分のリストのジェネレータを返す．
    ###
    ### これは for 文で使われることを想定している．
    def net_list(self) :
        for label, start_point, end_point in self.__net_list :
            yield label, start_point, end_point

    ### @brief label というラベルを持つネットがあるか調べる．
    ### @param[in] label 検索対象のラベル
    ### @retval True labelというラベルのネットがあった．
    def has_net(self, label) :
        return label in self.__net_dict

    ### @brief label というラベルを持つネットを返す．
    ### @param[in] label 検索対象のラベル
    ### @return (start, end) というタプルを返す．
    ###
    ### なければ None を返す．
    def net(self, label) :
        if label in self.__net_dict :
            return self.__net_dict[label]
        else :
            return None

    ### @brief ビア数を返す．
    @property
    def via_num(self) :
        return len(self.__via_list)

    ### @brief ビアを返す．
    ###
    ### これは for 文で使われることを想定している．
    def via_list(self) :
        for via in self.__via_list :
            yield via

    ### @brief label というラベルを持つビアがあるか調べる．
    ### @param[in] label 検索対象のラベル
    ### @retval True label というラベルのビアがあった．
    def has_via(self, label) :
        return label in self.__via_dict

    ### @brief label というラベルを持つビアを返す．
    ### @param[in] label 検索対象のラベル
    ###
    ### なければ None を返す．
    def via(self, label) :
        if label in self.__via_dict :
            return __via_dict[label]
        else :
            return None

    ### @brief 内容を書き出す．
    ###
    ### 主にデバッグ用
    def dump(self) :
        print('width  = {:2d}'.format(self.width))
        print('height = {:2d}'.format(self.height))
        print('depth  = {:2d}'.format(self.depth))

        for net_id, (label, start_point, end_point) in enumerate(self.net_list()) :
            print('[{:3d}] Net#{}: {} - {}'.format(net_id, label, start_point, end_point))

        for via_id, via in enumerate(self.via_list()) :
            print('[{:3d}] {}'.format(via_id, via))

# end of problem.py
