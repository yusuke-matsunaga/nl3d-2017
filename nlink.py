#! /usr/bin/env python3

### @file nlink.py
### @brief ナンバーリンクソルバのメインプログラム
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import sys
import os
import argparse

import nl3d
import nl3d.v2015
import nl3d.v2016
import nl3d.v2017

# コマンドラインパーサーの作成
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', type = str,
                    help = 'specify the output filename')
parser.add_argument('-l', '--var_limit', type = int,
                    help = 'specify the variable number limit')
parser.add_argument('-b', '--binary_encoding', action = 'store_true',
                    help = 'use binary_encoding')
parser.add_argument('-v', '--verbose', action = 'store_true',
                    help = 'set verbose mode')
parser.add_argument('input', type = str,
                    help = 'problem filename')

# コマンド行の解析
args = parser.parse_args()
if not args :
    exit(-1)

# 入力ファイル名
ifile = args.input
# 出力ファイル名 or None
ofile = args.output
# 変数数制約
if args.var_limit :
    var_limit = args.var_limit
else :
    var_limit = 0

# ２進符号化を用いる時に True にする．
binary_encoding = args.binary_encoding

verbose = args.verbose

# ファイルリーダーの作成
reader = nl3d.ADC_Reader()

with open(ifile, 'r') as fin :
    problem = reader.read_problem(fin)

    if verbose :
        print('SiZE:      {} x {} x {}'.format(problem.width, problem.height, problem.depth))
        print('# of nets: {}'.format(problem.net_num))
        print('# of vias: {}'.format(problem.via_num))

    graph = nl3d.Graph(problem)

    if problem.depth == 1 :
        # ADC2015 フォーマット
        status, solution = nl3d.v2015.solve_nlink(graph, var_limit, binary_encoding)
    elif problem.via_num > 0 :
        # ADC2016 フォーマット
        status, solution = nl3d.v2016.solve_nlink(graph, var_limit, binary_encoding)
    else :
        # ADC2017 フォーマット
        status, solution = nl3d.v2017.solve_nlink(graph, var_limit, binary_encoding)

    print(status)
    if status == 'OK' and ofile :
        with open(ofile, 'wt') as fout :
            solution.print(fout)
