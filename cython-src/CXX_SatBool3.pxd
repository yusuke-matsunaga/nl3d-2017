# @file CXX_SatBool3.pxd
# @brief CXX_SatBool3 の cython インターフェイス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

cdef extern from "ym/SatBool3.h" namespace "nsYm" :

    cdef enum SatBool3 :
        kB3False,
        kB3True,
        kB3X
