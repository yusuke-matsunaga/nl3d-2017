#! /usr/bin/env python3

## @file solve_nlink.py
# @brief solve_nlink の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.v2017.graph import Graph
from nl3d.v2017.cnfencoder import CnfEncoder


## @brief 問題を表すCNF式を生成する．
# @param[in] problem 問題(Problem)
# @return status, solution のタプルを返す．
#
# status は "OK", "NG", "Abort" のいずれか
# solution は "OK" の時は Solution のオブジェクト
# それ以外は None
def solve_nlink(problem, var_limit, binary_encoding) :
    graph = Graph(problem)

    print('plan_C')
    status, solution = plan_C(graph, var_limit, binary_encoding)
    if status == 'OK' :
        return status, solution

    return status, None


## @brief 最も簡単な戦略
def plan_C(graph, var_limit, binary_encoding) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = CnfEncoder(graph, solver_type, binary_encoding)

    enc.make_base_constraint(False)
    #enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve(var_limit)
