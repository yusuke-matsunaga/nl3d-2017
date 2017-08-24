#! /usr/bin/env python3

## @file satbool3.py
# @brief 3値のブール値を表すクラス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


from enum import Enum


## @brief SAT の結果を表す列挙型
#
# 真(B3True)，偽(B3False) の他に不定値を表す B3X
# がある．
class SatBool3(Enum) :
    B3X     =  0
    B3True  =  1
    B3False = -1


    ## @brief 否定を返す．
    def negate(self) :
        if self == SatBool3.B3X :
            return SatBool3.B3X
        elif self == SatBool3.B3True :
            return SatBool3.B3False
        elif self == SatBool3.B3False :
            return SatBool3.B3True
        else :
            assert False

    ## @brief 文字列表現を返す．
    def __repr__(self) :
        if self == SatBool3.B3X :
            return 'X(unknown)'
        elif self == SatBool3.B3True :
            return 'True'
        elif self == SatBool3.B3False :
            return 'False'
        else :
            assert False
