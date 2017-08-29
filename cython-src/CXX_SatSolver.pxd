# @file CXX_SatSolver.pxd
# @brief CXX_SatSolver の cython インターフェイス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from libcpp cimport bool
from libcpp.string cimport string
from CXX_vector cimport vector
from CXX_SatBool3 cimport SatBool3
from CXX_SatVarId cimport SatVarId
from CXX_SatLiteral cimport SatLiteral
from CXX_SatStats cimport SatStats

ctypedef unsigned int ymuint
ctypedef unsigned long ymuint64


cdef extern from "ym/SatSolver.h" namespace "nsYm" :

    # SatSolver クラスの cython バージョン
    cdef cppclass SatSolver :
        SatSolver(string sat_type, string sat_opt)
        SatVarId new_variable(bool decision)
        void add_clause(vector[SatLiteral]& lits)
        SatBool3 solve(vector[SatBool3]& model)
        SatBool3 solve(vector[SatLiteral]& assumptions, vector[SatBool3]& model)
        void stop()
        void timer_on(bool enable)
        ymuint64 set_max_conflict(ymuint64 val)
        bool sane()
        void get_stats(SatStats& stats)
        ymuint variable_num()
        ymuint clause_num()
        ymuint literal_num()
