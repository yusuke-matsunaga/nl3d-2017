#! /usr/bin/env python3

## @file nlsolver.py
# @brief NlSolver の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlgraph import NlGraph
from nl3d.nlcnfencoder import NlCnfEncoder
from nl3d.nlsolution import NlSolution

## @brief 問題を表すCNF式を生成する．
# @param[in] graph 問題を表すグラフ(NlGraph)
# @return status, solution のタプルを返す．
#
# status は "OK", "NG", "Abort" のいずれか
# solution は "OK" の時は NlSolution のオブジェクト
# それ以外は None
def solve_nlink(graph) :

    print('plan_A')
    status, solution = plan_A(graph)
    if status == 'OK' :
        return status, solution

    print('plan_B11')
    status, solution = plan_B11(graph)
    if status == 'OK' :
        return status, solution

    print('plan_B10')
    status, solution = plan_B10(graph)
    if status == 'OK' :
        return status, solution

    print('plan_B01')
    status, solution = plan_B01(graph)
    if status == 'OK' :
        return status, solution

    print('plan_C')
    status, solution = plan_C(graph)
    if status == 'OK' :
        return status, solution

    return status, None


## @brief 最も簡単な戦略
def plan_A(graph) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver_type)

    enc.make_base_constraint(True)
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve()


## @brief 最も簡単な戦略
def plan_B11(graph) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver_type)

    enc.make_base_constraint(False)
    enc.make_lshape_constraint()
    enc.make_yshape_constraint()
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve()


## @brief 最も簡単な戦略
def plan_B10(graph) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver_type)

    enc.make_base_constraint(False)
    enc.make_lshape_constraint()
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve()


## @brief 最も簡単な戦略
def plan_B01(graph) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver_type)

    enc.make_base_constraint(False)
    enc.make_yshape_constraint()
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve()


## @brief 最も簡単な戦略
def plan_C(graph) :

    solver_type = 'glueminisat2'

    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver_type)

    enc.make_base_constraint(False)
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    #enc.make_w2shape_constraint()

    # 問題を解く．
    return enc.solve()
