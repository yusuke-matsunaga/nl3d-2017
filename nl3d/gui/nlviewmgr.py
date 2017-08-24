#! /usr/bin/env python3

## @file nlviewmgr.py
# @brief
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2016 Yusuke Matsunaga
# All rights reserved.

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from nl3d.gui.nlviewwidget import NlViewWidget


class NlViewMgr(QObject) :

    ## @brief 初期化を行う．
    def __init__(self, parent = None) :

        super(NlViewMgr, self).__init__(parent)

        self.clear()


    ## @brief クリアする．
    def clear(self) :
        self._ViewList = []


    ## @brief 問題を設定する．
    def set_problem(self, problem) :
        self.clear()

        width = problem.width
        height = problem.height
        depth = problem.depth

        # 各層を表すウィジェットを生成する．
        for d in range(0, depth) :
            vw = NlViewWidget()
            vw.set_size(width, height)
            self._ViewList.append(vw)
            vw.show()

        # 終端の設定を行う．
        for net_id, (label, s, e) in enumerate(problem.net_list()) :
            self._set_terminal(s, net_id)
            self._set_terminal(e, net_id)

        # ビアの設定を行う．
        for via_id, via in enumerate(problem.via_list()) :
            self._set_via(via, via_id)


    ## @brief 問題と解を設定する．
    def set_solution(self, problem, solution) :
        self.set_problem(problem)

        width = problem.width
        height = problem.height
        depth = problem.depth

        for d in range(0, depth) :
            vw = self._ViewList[d]
            vw.set_solution_mode()
            for x in range(0, width) :
                for y in range(0, height) :
                    val = solution.val(x, y, d)
                    vw.set_val(x, y, val)


    ## @brief 終端の設定を行う．
    def _set_terminal(self, point, label) :
        x = point.x
        y = point.y
        z = point.z
        vw = self._ViewList[z]
        vw.set_terminal(x, y, label)


    ## @brief ビアの設定を行う．
    def _set_via(self, via, via_id) :
        label = via.label
        x = via.x
        y = via.y
        z1 = via.z1
        z2 = via.z2
        for z in range(z1, z2 + 1) :
            vw = self._ViewList[z]
            vw.set_via(via_id, x, y, label)
