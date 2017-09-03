#! /usr/bin/env python3

### @file adc2017_reader.py
### @brief ADC2017_Readerの定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import re
from nl3d.v2017.dimension import Dimension
from nl3d.v2017.problem import Problem
from nl3d.v2017.solution import Solution
from nl3d.v2017.point import Point

### @brief 3D版(ADC2017)のファイルを読み込むためのパーサークラス
###
### @code
### reader = ADC2017_Reader()
###
### fin1 = file('filename1', 'rt')
### if fin1 is not None :
###    problem = reader.read_problem(fin1)
###    ...
###
### fin2 = file('filename2', 'rt')
### if fin2 is not None :
###    solution = reader.read_solution(fin2)
###    ...
### @endcode
###
### という風に用いる．
class ADC2017_Reader :

    ### @brief 初期化
    def __init__(self) :
        # 正規表現のパタンを作る．
        # conmgr_master/server/nlcheck.py のパクリ
        self.__SIZE       = re.compile('SIZE +([0-9]+)X([0-9]+)X([0-9]+)', re.IGNORECASE)
        self.__LINE_NUM   = re.compile('LINE_NUM +([0-9]+)', re.IGNORECASE)
        self.__LINE_name  = re.compile('LINE#(\d+) +\((\d+),(\d+),(\d+)\)', re.IGNORECASE)
        self.__LINE_pos   = re.compile('[- ]\((\d+),(\d+),(\d+)\)', re.IGNORECASE)
        self.__LAYER_name = re.compile('LAYER ([0-9]+)', re.IGNORECASE)

    ### @brief 問題ファイルを読み込む．
    ### @param[in] fin ファイルオブジェクト
    ### @return Problem を返す．
    ###
    ### 読み込んだファイルの内容に誤りがある場合には None を返す．
    def read_problem(self, fin) :
        self.__problem = Problem()

        self.__nerr = 0
        self.__dim = None
        self.__line_num = 0

        self.__cur_line = ''
        self.__cur_lineno = 0

        self.__has_SIZE = False
        self.__has_LINE_NUM = False

        # ネット番号の重複チェック用の辞書
        # そのネット番号を定義している行番号を入れる．
        self.__net_dict = dict()

        # 基本的には1行づつ読み込んで処理していく．
        while True :
            # 1行を読み出し末尾の改行を取る．
            # ほぼ定石のコード
            line = fin.readline()
            self.__cur_lineno += 1
            if line == '' :
                # EOF
                break

            line = line.rstrip()
            if line == '' :
                # 空行を読み飛ばす．
                continue

            self.__cur_line = line

            # SIZE 行の処理
            if self.read_SIZE() :
                self.__problem.set_size(self.__dim)
                continue;

            # LINE_NUM 行の処理
            if self.read_LINE_NUM() :
                continue

            # LINE# 行の処理
            if self.read_LINE() :
                continue

            # それ以外はエラー
            self.error('syntax error')

        # エラーがなければ Problem を返す．
        if self.__nerr == 0 :
            return self.__problem
        else :
            return None

    ### @brief 解答ファイルを読み込む．
    ### @param[in] fin ファイルオブジェクト
    ### @return Solution を返す．
    ###
    ### 読み込んだファイルの内容に誤りがある場合には None を返す．
    def read_solution(self, fin) :
        self.__solution = Solution()

        self.__nerr = 0
        self.__has_SIZE = False

        self.__cur_lineno = 0
        self.__cur_y = 0
        self.__cur_z = 0

        # 基本的には1行づつ読み込んで処理していく．
        while True :
            # 1行を読み出し末尾の改行を取る．
            # ほぼ定石のコード
            line = fin.readline()
            self.__cur_lineno += 1
            if line == '' :
                # EOF
                break

            line = line.rstrip()
            if line == '' :
                # 空行を読み飛ばす．
                continue

            self.__cur_line = line

            # SIZE 行の処理
            if self.read_SIZE() :
                self.__solution.set_size(self.__dim)
                self.__cur_y = self.__dim.height
                continue;

            # LAYER 行の処理
            if self.read_LAYER() :
                continue

            # それ以外
            # 1行分の値が','で区切られている．
            if self.__cur_y == self.__dim.height :
                self.error("# of lines mismatch.")
                print('cur_y = {}'.format(self.__cur_y))
                continue

            val_list = line.split(',')
            n = len(val_list)
            if n != self.__dim.width :
                self.error('# of elements mismatch')
                continue
            for x in range(0, self.__dim.width) :
                val = int(val_list[x])
                self.__solution.set_val(x, self.__cur_y, self.__cur_z, val)
            self.__cur_y += 1
            if self.__cur_y == self.__dim.height :
                self.__cur_z += 1

        # エラーがなければ Solution を返す．
        if self.__nerr == 0 :
            return self.__solution
        else :
            return None

    ### @brief SIZE行の処理を行う．
    ### @retval True SIZE行だった．
    ### @retval False SIZE行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - すでに別のSIZE行があった．
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def read_SIZE(self) :
        # SIZE行のパターンにマッチするか調べる．
        m = self.__SIZE.match(self.__cur_line)
        if m is None :
            return False

        if self.__has_SIZE :
            # すでに別の SIZE行があった．
            self.error("Duplicated 'SIZE' line, previously defined at line {}".format(self.SIZE_lineno))
            return True

        width = int(m.group(1))
        height = int(m.group(2))
        depth = int(m.group(3))
        self.__dim = Dimension(width, height, depth)
        self.__has_SIZE = True
        self.SIZE_lineno = self.__cur_lineno
        return True

    ### LINE_NUM行の処理を行う．
    ### @retval True LINE_NUM行だった．
    ### @retval False LINE_NUM行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - すでに別の LINE_NUM 行があった．
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def read_LINE_NUM(self) :
        # LINE_NUM 行のパターンにマッチするか調べる．
        m = self.__LINE_NUM.match(self.__cur_line)
        if m is None :
            return False

        if self.__has_LINE_NUM :
            # すでに別の LINE_NUM 行があった．
            self.error("Duplicated 'LINE_NUM' line, previously defined at line {}".format(self.LINE_NUM_lineno))
            return True

        self.__line_num = int(m.group(1))
        self.__has_LINE_NUM = True
        self.LINE_NUM_lineno = self.__cur_lineno
        return True

    ### LINE 行の処理を行う．
    ### @retval True LINE行だった．
    ### @retval False LINE行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - SIZE 行が定義されていない．
    ### - LINE_NUM 行が定義されていない．
    ### - LINE# の番号が LINE_NUM の範囲外．
    ### - LINE# の番号が重複している．
    ### - 座標の値が SIZE の範囲外．
    ### - 指定されている座標の数が2つ以外(syntax error)．
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def read_LINE(self) :
        # LINE行のパターンにマッチするか調べる．
        m = self.__LINE_name.match(self.__cur_line)
        if m is None :
            return False

        if not self.__has_SIZE :
            # SIZE 行がない．
            self.error("Missing 'SIZE' before 'LINE'")
            return True

        if not self.__has_LINE_NUM :
            # LINE_NUM 行がない．
            self.error("Missing 'LINE_NUM' before 'LINE'")
            return True

        # 線分番号を得る．
        net_id = int(m.groups()[0])

        # 番号が範囲内にあるかチェックする．
        if not 1 <= net_id <= self.__line_num :
            self.error('LINE#{} is out of range'.format(net_id))
            return True

        # 重複していないか調べる．
        if net_id in self.__net_dict :
            prev = self.__net_dict[net_id]
            self.error('Duplicated LINE#{}, previously defined at line {}.'.format(net_id, prev))
            return True
        self.__net_dict[net_id] = self.__cur_lineno

        # 線分の始点と終点を求める．
        count = 0
        for m in self.__LINE_pos.finditer(self.__cur_line) :
            x = int(m.group(1))
            y = int(m.group(2))
            z = int(m.group(3)) - 1 # ADC2017フォーマットでは層番号は1から始まる．
            # 範囲チェックを行う．
            if not self.check_range(x, y, z) :
                return True

            if count == 0 :
                start_point = Point(x, y, z)
            elif count == 1 :
                end_point = Point(x, y, z)
            else :
                break
            count += 1

        if count != 2 :
            self.error('Syntax error')
            return True

        self.__problem.add_net(net_id, start_point, end_point)
        return True

    ### LAYER 行の処理を行う．
    ### @retval True LAYER行だった．
    ### @retval False LAYER行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - LAYER 番号が異なる．
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def read_LAYER(self) :
        # LAYER行のパターンにマッチするか調べる．
        m = self.__LAYER_name.match(self.__cur_line)
        if m is None :
            return False

        if not self.__has_SIZE :
            # SIZE 行がない．
            self.error("'SIZE' does not exist.")
            return True

        if self.__cur_y != self.__dim.height :
            self.error("# of lines mismatch.")
            return True

        lay = int(m.group(1))
        expected = self.__cur_z + 1
        if lay != expected :
            self.error('Illegal LAYER ID {}, {} expected.'.format(lay, expected))
            return True

        self.__cur_y = 0
        return True

    ### (x, y, z) が範囲内にあるか調べる
    ### @param[in] x, y, z 座標
    ### @retval True 範囲内だった．
    ### @retval False 範囲外だった．
    def check_range(self, x, y, z) :
        if not 0 <= x < self.__dim.width :
            self.error('X({}) is out of range.'.format(x))
            return False

        if not 0 <= y < self.__dim.height :
            self.error('Y({}) is out of range.'.format(y))
            return False

        if not 0 <= z < self.__dim.depth :
            self.error('Z({}) is out of range.'.format(z + 1))
            return False

        return True

    ### エラー処理
    ### @param[in] msg エラーメッセージ
    ###
    ### nerr の値が加算される．
    def error(self, msg) :
        print('Error at line {}: {}'.format(self.__cur_lineno, msg))
        print('    {}'.format(self.__cur_line))
        self.__nerr += 1

# end of adc2017_reader.py
