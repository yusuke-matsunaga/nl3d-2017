#! /usr/bin/env python3
#
# @file conv.py
# @brief
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

import os
import re
import sys
from nl3d import ADC_Reader

def conv2d(fin, fout) :
    problem = reader.read_problem(fin)
    if problem.depth > 1 :
        print('{} is not a 2D problem'.format(ifile))
        exit(-1)

    print('SIZE {}X{}'.format(problem.width, problem.height), file = fout)
    print('LINE_NUM {}'.format(problem.net_num), file = fout)
    for label, start_point, end_point in problem.net_list() :
        print('LINE#{} ({},{})-({},{})'.format(label, start_point.x, start_point.y, end_point.x, end_point.y), file = fout)

if len(sys.argv) < 2 :
    print('USAGE: conv.py <filename> ...')
    exit(-1)

reader = ADC_Reader()

for file in sys.argv[1:] :
    bname = os.path.basename(file)
    print('file = {}, basename = {}'.format(file, bname))
    with open(file, 'rt') as fin :
        with open(bname, 'wt') as fout :
            conv2d(fin, fout)
