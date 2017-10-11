#! /usr/bin/env python3

### @file __init__.py
### @brief nl3d パッケージの初期化ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

from nl3d.point import Point
from nl3d.dimension import Dimension
from nl3d.via import Via
from nl3d.problem import Problem
from nl3d.graph import Graph
from nl3d.solution import Solution


### @brief ADC2016/ADC2017 フォーマットの問題を読み込む．
### @param[in] fin ファイルオブジェクト
### @return Problem を返す．
###
### 読み込んだファイルの内容に誤りがある場合には None を返す．
###
### @code
### fin1 = file('filename1', 'r')
### if fin1 is not None :
###    problem = read_problem(fin1)
###    ...
### @endcode
def read_problem(fin) :
    from nl3d.adc_reader import ADC_Reader
    reader = ADC_Reader()
    return reader.read_problem(fin)

### @brief 解答ファイルを読み込む．
### @param[in] fin ファイルオブジェクト
### @return Solution を返す．
###
### 読み込んだファイルの内容に誤りがある場合には None を返す．
###
### @code
### fin = file('filename', 'r')
### if fin is not None :
###    solution = read_solution(fin)
###    ...
### @endcode
def read_solution(fin) :
    from nl3d.adc_reader import ADC_Reader
    reader = ADC_Reader()
    return reader.read_solution(fin)
