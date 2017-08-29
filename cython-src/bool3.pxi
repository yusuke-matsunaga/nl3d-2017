# @file bool3.pxi
# @brief bool3 の python インターフェイス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from enum import Enum
from CXX_SatBool3 cimport SatBool3, kB3X, kB3True, kB3False

# @brief SatBool3 の Python バージョン
#
# もとの C++ の列挙型とは別に Python の拡張型として
# 定義する．
# 相互の変換関数を用意することでシームレスに使えるようにする．
class Bool3(Enum) :
    UNKNOWN = 0
    TRUE    = 1
    FALSE   = 2

    # @brief 否定する．
    def negate(self) :
        if self == Bool3.TRUE :
            return Bool3.FALSE
        elif self == Bool3.FALSE :
            return Bool3.TRUE
        elif self == Bool3.UNKNOWN :
            return Bool3.UNKNOWN
        else :
            assert False

    # @brief 文字列表現を返す．
    def __repr__(self) :
        if self == Bool3.UNKNOWN :
            return 'UNKNOWN'
        elif self == Bool3.TRUE :
            return 'TRUE'
        elif self == Bool3.FALSE :
            return 'FALSE'
        else :
            assert False


# @brief Python の Bool3 を C++ の SatBool3 に変換する．
cdef SatBool3 from_bool3(val) :
    if val == Bool3.UNKOWN :
        return kB3X
    elif val == Bool3.TRUE :
        return kB3True
    elif val == Bool3.FALSE :
        return kB3False
    else :
        assert False


# @brief C++ の SatBool3 を Python の Bool3 に変換する．
def to_bool3(SatBool3 c_val) :
    if c_val == kB3X :
        return Bool3.UNKOWN
    elif c_val == kB3True :
        return Bool3.TRUE
    elif c_val == kB3False :
        return Bool3.FALSE
    else :
        assert False
