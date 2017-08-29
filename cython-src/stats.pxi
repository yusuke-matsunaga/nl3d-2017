# @file stats.pxi
# @brief Stats の python インターフェイス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from CXX_SatStats cimport SatStats


## @brief 統計情報を表すクラス
cdef class Stats :

    # C++ 版の本体
    cdef SatStats _body

    ## @brief 初期化
    def __init__(Stats self) :
        pass

    ## @brief 内容をクリアする．
    def clear(Stats self) :
        self._body.clear()

    ## @brief restart の回数
    @property
    def reestart(Stats self) :
        return self._body.mRestart

    ## @brief 変数の数
    @property
    def variable_num(Stats self) :
        return self._body.mVarNum

    ## @brief 制約節の数
    @property
    def constr_clause_num(Stats self) :
        return self._body.mConstrClauseNum

    ## @brief 制約節のりテラル数
    @property
    def constr_literal_num(Stats self) :
        return self._body.mConstrLitNum

    ## @brief 学習節の数
    @property
    def learnt_clause_num(Stats self) :
        return self._body.mLearntClauseNum

    ## @brief 学習節のリテラル数
    @property
    def learnt_literal_num(Stats self) :
        return self._body.mLearntLitNum

    ## @brief コンフリクト数
    @property
    def conflict_num(Stats self) :
        return self._body.mConflictNum

    ## @brief 決定分岐数
    @property
    def decision_num(Stats self) :
        return self._body.mDecisionNum

    ## @brief 含意数
    @property
    def propagation_num(Stats self) :
        return self._body.mPropagationNum

    ## @brief コンフリクト数の制限値
    @property
    def conflict_limit(Stats self) :
        return self._body.mConflictLimit

    ## @brief 学習節の制限値
    @property
    def learnt_limit(Stats self) :
        return self._body.mLearntLimit

cdef to_stats(SatStats c_stats) :
    ans = Stats()
    ans._body = c_stats
    return ans
