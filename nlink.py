#! /usr/bin/env python3
#
# @file test.py
# @brief
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

import sys
import os
import argparse

sys.path.append('./')

import nl3d

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', type = str,
                    help = 'specify the output filename')
parser.add_argument('-l', '--var_limit', type = int,
                    help = 'specify the variable number limit')
parser.add_argument('-b', '--binary_encoding', action = 'store_true',
                    help = 'use binary_encoding')
parser.add_argument('input', type = str,
                    help = 'problem filename')

args = parser.parse_args()
if not args :
    exit(-1)

ifile = args.input
ofile = args.output
if args.var_limit :
    var_limit = args.var_limit
else :
    var_limit = 0

binary_encoding = args.binary_encoding

reader = nl3d.ADC2017_Reader()

with open(ifile, 'r') as fin :
    problem = reader.read_problem(fin)
    graph = nl3d.NlGraph(problem)

    status, solution = nl3d.solve_nlink(graph, var_limit, binary_encoding)

    print(status)
    if status == 'OK' :
        if ofile :
            with open(ofile, 'wt') as fout :
                solution.print(fout)
