#! /usr/bin/env python3

### @file nlview.py
### @brief ナンバーリンクの問題と解答を表示するプログラム
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import sys
import os
import argparse

import nl3d
import nl3d.gui

from PyQt5.QtWidgets import *

# コマンドラインパーサーの作成
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--answer', type = str,
                    help = 'specify the answer filename')
parser.add_argument('input', type = str,
                    help = 'problem filename')

# コマンド行の解析
args = parser.parse_args()
if not args :
    exit(-1)

# 入力ファイル名
ifile = args.input
# 出力ファイル名 or None
ofile = args.answer

# ファイルリーダーの作成
reader = nl3d.ADC_Reader()

problem = None
solution = None
with open(ifile, 'rt') as fin :
    problem = reader.read_problem(fin)
    if not problem :
        print('{}: read failed.'.format(ifile))
        exit(-1)

    if ofile :
        with open(ofile, 'rt') as fin2 :
            solution = reader.read_solution(fin2)
            if not solution :
                print('{}: read failed.'.format(ofile))
                exit(-1)

app = QApplication(sys.argv)
viewmgr = nl3d.gui.ViewMgr()

if solution :
    viewmgr.set_solution(problem, solution)
else :
    viewmgr.set_problem(problem)

app.exec_()
