#! /usr/bin/env python3

## @file satsolver.py
# @brief SAT ソルバ用のインターフェイスクラス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


from enum import Enum

## @brief SAT ソルバのインターフェイスを定義したスケルトン
class SatSolver :

    # @brief 初期化
    def __init__(self) :
        pass


    ## @brief 変数を作る．
    # @return 変数番号を返す．
    #
    # 変数番号は 1 から始まる．
    def new_variable(self) :
        pass


    ## @brief 節を追加する．
    # @param[in] lit_list 節のリテラルのリスト
    #
    # リテラルは 0 以外の整数で，絶対値が番号を
    # 符号が極性を表す．
    # たとえば 3 なら 3番目の変数の肯定
    # -1 なら 1番目の変数の否定を表す．
    def add_clause(self, lit_list) :
        pass


    ## @brief SAT問題を解く．
    # @param[in] assumption_list 仮定する割り当てリスト
    # @return (result, model) を返す．
    #
    # - result は SatBool3
    # - model は結果の各変数に対する値を格納したリスト
    #   変数番号が 1番の変数の値は model[1] に入っている．
    #   値は SatBool3
    def solve(self, assumption_list) :
        pass
