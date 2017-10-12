### @file varid.pxi
### @brief VarId の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.


from CXX_SatVarId cimport SatVarId


### @brief 変数番号を表すクラス
###
### C++ の SatVarId とは別の拡張型として定義して
### 相互の変換関数を用意する．
cdef class VarId :

    # 変数番号の実体
    cdef int __val

    ### @brief 初期化
    ### @param[in] val 値
    def __init__(VarId self, val = -1) :
        self.__val = val

    ### @brief 値を返す．
    def val(VarId self) :
        return self.__val

    ### @brief 適正な値を持っている時 True を返す．
    def is_valid(VarId self) :
        return self.__val >= 0

    ### @brief ハッシュ関数
    def __hash__(VarId self) :
        return self.__val

    ### @brief 文字列演算子
    def __repr__(VarId self) :
        return 'V{}'.format(self.__val)


### @brief 比較関数
def __richcmp__(VarId self,
                VarId other) :
    return self.__val - other.__val


### @brief Python の VarId を C++ の SatVarId に変換する．
### @param[in] varid Python バージョンの VarId
cdef SatVarId from_varid(varid) :
    return SatVarId(varid.__val)


### @brief C++ の SatVarId を Python の VarId に変換する．
### @param[in] c_varid C++ バージョンの SatVarid
cdef to_varid(SatVarId c_varid) :
    return VarId(c_varid.val())
