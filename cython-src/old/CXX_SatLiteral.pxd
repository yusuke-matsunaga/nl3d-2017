# @file CXX_SatLiteral.pxd
# @brief CXX_SatLiteral の cython インターフェイス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from libcpp cimport bool
from CXX_SatVarId cimport SatVarId

ctypedef unsigned int ymuint


cdef extern from "ym/SatLiteral.h" namespace "nsYm" :

    # SatLiteral クラスの cython バージョン
    cdef cppclass SatLiteral :
        SatLiteral()
        SatLiteral(SatVarId varid, bool inv)
        void set(SatVarId varid, bool inv)
        SatVarId varid()
        bool is_positive()
        bool is_negative()
        SatLiteral make_positive()
        SatLiteral make_negative()
        ymuint index()
