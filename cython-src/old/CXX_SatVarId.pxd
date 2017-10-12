# @file CXX_SatVarId.pxd
# @brief CXX_SatVarId の cython インターフェイス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from libcpp cimport bool
ctypedef unsigned int ymuint


cdef extern from "ym/SatVarId.h" namespace "nsYm" :

    # SatVarId クラスの cython バージョン
    cdef cppclass SatVarId :
        SatVarId()
        SatVarId(ymuint val)
        bool is_valid()
        ymuint val()
