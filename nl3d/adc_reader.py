#! /usr/bin/env python3

### @file adc_reader.py
### @brief ADC_Reader の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import re
from nl3d.dimension import Dimension
from nl3d.point import Point
from nl3d.via import Via
from nl3d.problem import Problem
from nl3d.solution import Solution

# 正規表現のパタンを作る．
# もともとは conmgr/server/nlcheck.py のパクリ
SIZE2D     = re.compile('^SIZE +([0-9]+)X([0-9]+)$', re.IGNORECASE)
SIZE3D     = re.compile('^SIZE +([0-9]+)X([0-9]+)X([0-9]+)$', re.IGNORECASE)
LINE_NUM   = re.compile('^LINE_NUM +([0-9]+)$', re.IGNORECASE)
LINE2D     = re.compile('^LINE#(\d+) +\((\d+),(\d+)\)[- ]\((\d+),(\d+)\)$', re.IGNORECASE)
LINE3D     = re.compile('^LINE#(\d+) +\((\d+),(\d+),(\d+)\)[- ]\((\d+),(\d+),(\d+)\)$', re.IGNORECASE)
VIA3D_name = re.compile('^VIA#([a-z]+) +(\((\d+),(\d+),(\d+)\))+', re.IGNORECASE)
VIA3D_pos  = re.compile('[- ]\((\d+),(\d+),(\d+)\)$', re.IGNORECASE)
LAYER_name = re.compile('^LAYER ([0-9]+)$', re.IGNORECASE)


### @brief ADC2016/ADC2017 フォーマットの読み込み用クラス
###
### @code
### reader = ADC_Reader()
###
### fin1 = file('filename1', 'r')
### if fin1 is not None :
###    problem = reader.read_problem(fin1)
###    ...
###
### fin2 = file('filename2', 'r')
### if fin2 is not None :
###    solution = reader.read_solution(fin2)
###    ...
### @endcode
###
### という風に用いる．
###
### ADC2015 フォーマットは2Dバージョンなので SIZE行とLINE行が異なる．
### SIZE行は最初に現れるのでそこで判断する．
### ADC2016 フォーマットには VIA# 行があり ADC2017 フォーマットには VIA# 行がない．<br>
### 見かけ上の違いはそれだけなので同一のコードを用いる．
class ADC_Reader :

    ### @brief 初期化
    def __init__(self) :
        pass

    ### @brief 問題ファイルを読み込む．
    ### @param[in] fin ファイルオブジェクト
    ### @return Problem を返す．
    ###
    ### 読み込んだファイルの内容に誤りがある場合には None を返す．
    def read_problem(self, fin) :
        self.__problem = Problem()

        self.__2D = False

        self.__nerr = 0
        self.__dim = None
        self.__line_num = 0
        self.__via_num = 0

        self.__cur_line = ''
        self.__cur_lineno = 0

        self.__has_SIZE = False
        self.__has_LINE_NUM = False

        # ネット番号の重複チェック用の辞書
        # そのネット番号を定義している行番号を入れる．
        self.__net_dict = dict()

        # ビアラベルの重複チェック用の辞書
        # そのビアを定義している行番号を入れる．
        self.__via_dict = dict()

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

            # SIZE(2D) 行の処理
            if self.__read_SIZE2D() :
                self.__problem.set_size(self.__dim)
                continue;

            # SIZE(3D) 行の処理
            if self.__read_SIZE3D() :
                self.__problem.set_size(self.__dim)
                continue;

            # LINE_NUM 行の処理
            if self.__read_LINE_NUM() :
                continue

            # LINE# 行の処理
            if self.__read_LINE() :
                continue

            # VIA# 行の処理
            if self.__read_VIA() :
                continue

            # それ以外はエラー
            self.__error('syntax error')

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
            if self.__read_SIZE() :
                self.__solution.set_size(self.__dim)
                self.__cur_y = self.__dim.height
                continue;

            # LAYER 行の処理
            if self.__read_LAYER() :
                continue

            # それ以外
            # 1行分の値が','で区切られている．
            if self.__cur_y == self.__dim.height :
                self.__error("# of lines mismatch.")
                print('_cur_y = {}'.format(self.__cur_y))
                continue

            val_list = line.split(',')
            n = len(val_list)
            if n != self.__dim.width :
                self.__error('# of elements mismatch')
                continue

            for x in range(0, self.__dim.width) :
                point = Point(x, self.__cur_y, self.__cur_z)
                val = int(val_list[x])
                self.__solution.set_val(point, val)
            self.__cur_y += 1
            if self.__cur_y == self.__dim.height :
                self.__cur_z += 1

        # エラーがなければ Problem を返す．
        if self.__nerr == 0 :
            return self.__solution
        else :
            return None

    ### @brief SIZE(2D)行の処理を行う．
    ### @retval True SIZE行だった．
    ### @retval False SIZE行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - すでに別のSIZE行があった．
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def __read_SIZE2D(self) :
        # SIZE行のパターンにマッチするか調べる．
        m = SIZE2D.match(self.__cur_line)
        if m is None :
            return False

        if self.__has_SIZE :
            # すでに別の SIZE行があった．
            self.__error("Duplicated 'SIZE' line, previously defined at line {}".format(self.SIZE_lineno))
            return True

        width = int(m.group(1))
        height = int(m.group(2))
        depth = 1
        self.__dim = Dimension(width, height, depth)
        self.__has_SIZE = True
        self.__2D = True
        self.SIZE_lineno = self.__cur_lineno
        return True

    ### @brief SIZE(3D)行の処理を行う．
    ### @retval True SIZE行だった．
    ### @retval False SIZE行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - すでに別のSIZE行があった．
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def __read_SIZE3D(self) :
        # SIZE行のパターンにマッチするか調べる．
        m = SIZE3D.match(self.__cur_line)
        if m is None:
            return False

        if self.__has_SIZE :
            # すでに別の SIZE行があった．
            self.__error("Duplicated 'SIZE' line, previously defined at line {}".format(self.SIZE_lineno))
            return True

        width = int(m.group(1))
        height = int(m.group(2))
        depth = int(m.group(3))
        self.__dim = Dimension(width, height, depth)
        self.__has_SIZE = True
        self.__2D = False
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
    def __read_LINE_NUM(self) :
        # LINE_NUM 行のパターンにマッチするか調べる．
        m = LINE_NUM.match(self.__cur_line)
        if m is None :
            return False

        if self.__has_LINE_NUM :
            # すでに別の LINE_NUM 行があった．
            self.__error("Duplicated 'LINE_NUM' line, previously defined at line {}".format(self.LINE_NUM_lineno))
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
    def __read_LINE(self) :
        # LINE行のパターンにマッチするか調べる．
        if self.__2D :
            m = LINE2D.match(self.__cur_line)
        else :
            m = LINE3D.match(self.__cur_line)
        if m is None :
            return False

        if not self.__has_SIZE :
            # SIZE 行がない．
            self.__error("Missing 'SIZE' before 'LINE'")
            return True

        if not self.__has_LINE_NUM :
            # LINE_NUM 行がない．
            self.__error("Missing 'LINE_NUM' before 'LINE'")
            return True

        # 線分番号を得る．
        #net_id = int(m.groups()[0])
        net_id = int(m.group(1))

        # 番号が範囲内にあるかチェックする．
        if not 1 <= net_id <= self.__line_num :
            self.__error('LINE#{} is out of range'.format(net_id))
            return True

        # 重複していないか調べる．
        if net_id in self.__net_dict :
            prev = self.__net_dict[net_id]
            self.__error('Duplicated LINE#{}, previously defined at line {}.'.format(net_id, prev))
            return True
        self.__net_dict[net_id] = self.__cur_lineno

        # 線分の始点と終点を求める．
        if self.__2D :
            x0 = int(m.group(2))
            y0 = int(m.group(3))
            z0 = 0
            x1 = int(m.group(4))
            y1 = int(m.group(5))
            z1 = 0
        else :
            x0 = int(m.group(2))
            y0 = int(m.group(3))
            z0 = int(m.group(4)) - 1
            x1 = int(m.group(5))
            y1 = int(m.group(6))
            z1 = int(m.group(7)) - 1

        # 範囲チェックを行う．
        if not self.__check_range(x0, y0, z0) :
            return True
        start_point = Point(x0, y0, z0)

        if not self.__check_range(x1, y1, z1) :
            return True
        end_point = Point(x1, y1, z1)

        self.__problem.add_net(net_id, start_point, end_point)
        return True

    ### @brief VIA行を読み込む．
    ### @retval True VIA行だった．
    ### @retval False VIA行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - SIZE行が定義されていない．
    ### - 座標または層番号が範囲外だった．
    ### - 層ごとのX座標またはY座標が異なっている．
    ### - 層番号が連続していない．(順不同)
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def __read_VIA(self) :
        # VIA行のパターンにマッチするか調べる．
        m = VIA3D_name.match(self.__cur_line)
        if m is None :
            return False

        if not self.__has_SIZE :
            # SIZE 行がない．
            self.__error("Missing 'SIZE' before 'VIA'")
            return True

        via_label = m.groups()[0]

        # ラベルが重複していないか調べる．
        if via_label in self.__via_dict :
            prev = self.__via_dict[via_label]
            self.__error('Duplicated VIA#{}, previously defined at line {}'.format(via_label, prev))
            return True
        self.__via_dict[via_label] = self.__cur_lineno

        first_time = True
        z_list = []
        for m in VIA3D_pos.finditer(self.__cur_line) :
            x, y, z = m.groups()
            x = int(x)
            y = int(y)
            z = int(z) - 1 # ファイルフォーマットでは層番号は1から始まる．
            # 範囲チェックを行う．
            if not self.__check_range(x, y, z) :
                return True

            if first_time :
                x0 = x
                y0 = y
                first_time = False
            else :
                # すべての層で x, y 座標は同じでなければならない．
                if x != x0 :
                    self.__error("X({}) is differnt from the first point's X({})".format(x, x0))
                    return True
                if y != y0 :
                    self.__error("Y({}) is differnt from the first point's Y({})".format(y, y0))
                    return True
                # 同じことが確認されたら x, y に用はない．
            z_list.append(z)

        # z のリストをソートする．
        z_list.sort()
        n = len(z_list)
        z1 = z_list[0]
        z2 = z_list[n - 1]
        if (z2 - z1) != (n - 1) :
            # z1 から z2 の連続した区間になっていない．
            self.__error('Some layers are missing')
            return True

        via = Via(via_label, x0, y0, z1, z2)
        self.__problem.add_via(via)
        return True

    ### LAYER 行の処理を行う．
    ### @retval True LAYER行だった．
    ### @retval False LAYER行ではなかった．
    ###
    ### 以下の場合にエラーとなる．
    ### - LAYER 番号が異なる．
    ###
    ### 返り値の真偽はエラーの有無とは関係ない．
    def __read_LAYER(self) :
        # LAYER行のパターンにマッチするか調べる．
        m = LAYER_name.match(self.__cur_line)
        if m is None :
            return False

        if not self.__has_SIZE :
            # SIZE 行がない．
            self.__error("'SIZE' does not exist.")
            return True

        if self.__cur_y != self.__dim.height :
            self.__error("# of lines mismatch.")
            return True

        lay = int(m.group(1))
        expected = self.__cur_z + 1
        if lay != expected :
            self.__error('Illegal LAYER ID {}, {} expected.'.format(lay, expected))
            return True

        self.__cur_y = 0
        return True

    ### (x, y, z) が範囲内にあるか調べる
    ### @param[in] x, y, z 座標
    ### @retval True 範囲内だった．
    ### @retval False 範囲外だった．
    def __check_range(self, x, y, z) :
        if not 0 <= x < self.__dim.width :
            self.__error('X({}) is out of range.'.format(x))
            return False

        if not 0 <= y < self.__dim.height :
            self.__error('Y({}) is out of range.'.format(y))
            return False

        if not 0 <= z < self.__dim.depth :
            self.__error('Z({}) is out of range.'.format(z + 1))
            return False

        return True

    ### エラー処理
    ### @param[in] msg エラーメッセージ
    ###
    ### self.__nerr の値が加算される．
    def __error(self, msg) :
        print('Error at line {}: {}'.format(self.__cur_lineno, msg))
        print('    {}'.format(self.__cur_line))
        self.__nerr += 1

# end of adc2016_reader.py
