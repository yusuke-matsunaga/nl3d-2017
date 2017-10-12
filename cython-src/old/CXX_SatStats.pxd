# @file CXX_SatStats.pxd
# @brief CXX_SatStats の cython インターフェイス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

ctypedef unsigned int ymuint
ctypedef unsigned long ymuint64


cdef extern from "ym/SatStats.h" namespace "nsYm" :

    cdef cppclass SatStats :
        SatStats()
        void clear()
        ymuint mRestart
        ymuint mVarNum
        ymuint64 mConstrClauseNum
        ymuint64 mConstrLitNum
        ymuint64 mLearntClauseNum
        ymuint64 mLearntLitNum
        ymuint64 mConflictNum
        ymuint64 mDecisionNum
        ymuint64 mPropagationNum
        ymuint64 mConflictLimit
        ymuint64 mLearntLimit
