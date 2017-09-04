#! /usr/bin/env python3

## @file nlsolver.py
# @brief NlSolver の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlgraph import NlNode, NlEdge, NlGraph
from nl3d.nlcnfencoder import NlCnfEncoder
from nl3d.nlsolution import NlSolution
from nl3d.sat.satsolver import SatSolver
from nl3d.sat.satbool3 import SatBool3

## @brief 問題を表すCNF式を生成する．
# @param[in] graph 問題を表すグラフ(NlGraph)
# @return status, solution のタプルを返す．
#
# status は "OK", "NG", "Abort" のいずれか
# solution は "OK" の時は NlSolution のオブジェクト
# それ以外は None
def solve_nlink(graph) :

    status, solution = plan_A(graph)
    if status == "OK" :
        return status, solution

    status, solution = plan_B(graph)
    if status == "OK" :
        return status, solution

    return status, None


## @brief 最も簡単な戦略
def plan_A(graph) :

    solver = SatSolver('minisat_static')

    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver)

    enc.make_base_constraint(True)
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    enc.make_w2shape_constraint()

    # SAT問題を解く．
    result, model = solver.solve()

    if result == SatBool3.B3True :
        # 解けた．

        # SATモデルから解を作る．
        solution = enc.model_to_solution(model)
        return "OK", solution

    elif result == SatBool3.B3False :
        # 解けなかった．
        return "NG", None

    elif result == SatBool3.B3X :
        # アボートした．
        return "Abort", None


## @brief 最も簡単な戦略
def plan_B(graph) :

    solver = SatSolver('minisat_static')

    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver)

    enc.make_base_constraint(False)
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    enc.make_w2shape_constraint()

    # SAT問題を解く．
    result, model = solver.solve()

    if result == SatBool3.B3True :
        # 解けた．

        # SATモデルから解を作る．
        solution = enc.model_to_solution(model)
        return "OK", solution

    elif result == SatBool3.B3False :
        # 解けなかった．
        return "NG", None

    elif result == SatBool3.B3X :
        # アボートした．
        return "Abort", None
