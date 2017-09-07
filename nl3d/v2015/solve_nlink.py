#! /usr/bin/env python3

## @file nlsolver.py
# @brief NlSolver の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.v2015.cnfencoder import CnfEncoder


## @brief 問題を表すCNF式を生成する．
# @param[in] graph 問題を表すグラフ(Graph)
# @return status, solution のタプルを返す．
#
# status は "OK", "NG", "Abort" のいずれか
# solution は "OK" の時は NlSolution のオブジェクト
# それ以外は None
def solve_nlink(graph, var_limit, binary_encoding) :

    print('plan_A(v2015)')
    status, solution = plan_A(graph, var_limit, binary_encoding)
    if status == 'OK' :
        return status, solution

    print('plan_B11(v2015)')
    status, solution = plan_B11(graph, var_limit, binary_encoding)
    if status == 'OK' :
        return status, solution

    print('plan_B10(v2015)')
    status, solution = plan_B10(graph, var_limit, binary_encoding)
    if status == 'OK' :
        return status, solution

    print('plan_B01(v2015)')
    status, solution = plan_B01(graph, var_limit, binary_encoding)
    if status == 'OK' :
        return status, solution

    print('plan_C(v2015)')
    status, solution = plan_C(graph, var_limit, binary_encoding)
    if status == 'OK' :
        return status, solution

    return status, None


## @brief 最も簡単な戦略
def plan_A(graph, var_limit, binary_encoding) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = CnfEncoder(graph, solver_type, binary_encoding)

    enc.make_base_constraint(True)

    #enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve(var_limit)


## @brief 最も簡単な戦略
def plan_B11(graph, var_limit, binary_encoding) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = CnfEncoder(graph, solver_type, binary_encoding)

    enc.make_base_constraint(False)
    enc.make_lshape_constraint()
    enc.make_yshape_constraint()

    #enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve(var_limit)


## @brief 最も簡単な戦略
def plan_B10(graph, var_limit, binary_encoding) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = CnfEncoder(graph, solver_type, binary_encoding)

    enc.make_base_constraint(False)
    enc.make_lshape_constraint()

    #enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve(var_limit)


## @brief 最も簡単な戦略
def plan_B01(graph, var_limit, binary_encoding) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = CnfEncoder(graph, solver_type, binary_encoding)

    enc.make_base_constraint(False)
    enc.make_yshape_constraint()

    #enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve(var_limit)


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
