#! /usr/bin/env python3

## @file satsolver.py
# @brief SAT ソルバ用のインターフェイスクラス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


from enum import Enum
import tempfile
import os
import subprocess

from nl3d.sat.satbool3 import SatBool3


## @brief SAT ソルバを表すクラス
#
# このクラスは内部でSATソルバのプログラムを呼び出している．
# 同じインターフェイスで内部で SAT を解くクラスを(主にC++で)
# 実装しても良い．
class SatSolver :

    ## @brief 初期化
    # @param[in] satprog SATソルバのプログラム名
    def __init__(self, satprog) :
        self._var_count = 0
        self._clause_list = []
        self._satprog = satprog
        # デバッグフラグ
        self._debug = False


    ## @brief 変数を作る．
    # @return 変数番号を返す．
    #
    # 変数番号は 1 から始まる．
    def new_variable(self) :
        self._var_count += 1
        return self._var_count


    ## @brief 節を追加する．
    # @param[in] args 節のリテラルのリスト
    #
    # リテラルは 0 以外の整数で，絶対値が番号を
    # 符号が極性を表す．
    # たとえば 3 なら 3番目の変数の肯定
    # -1 なら 1番目の変数の否定を表す．
    def add_clause(self, *args) :
        if len(args) == 1 :
            arg0 = args[0]
            if isinstance(arg0, int) :
                # singleton の場合
                lit = arg0
                if self._check_lit(lit) :
                    self._clause_list.append([lit])
            elif isinstance(arg0, list) :
                # リストの場合
                for lit in arg0 :
                    if not self._check_lit(lit) :
                        return
                self._clause_list.append(arg0)
        else :
            for lit in args :
                if not self._check_lit(lit) :
                    return
            self._clause_list.append(args)


    ## @brief SAT問題を解く．
    # @param[in] assumption_list 仮定する割り当てリスト
    # @return (result, model) を返す．
    #
    # - result は SatBool3
    # - model は結果の各変数に対する値を格納したリスト
    #   変数番号が 1番の変数の値は model[1] に入っている．
    #   値は SatBool3
    def solve(self, assumption_list = []) :

        # デフォルトの返り値
        result = SatBool3.B3X
        model = []

        # dimacs 形式のファイルを作る．
        # fh は使わない．
        (fh, dimacs_file) = tempfile.mkstemp()
        fout = open(dimacs_file, 'w')
        if not fout :
            print('Error: could not create {} for DIMACS input.'.format(dimacs_file))
            return

        # ヘッダを書き出す．
        var_num = self._var_count
        clause_num = len(self._clause_list)
        fout.write('p cnf {} {}\n'.format(var_num, clause_num))

        # 節の内容を書き出す．
        for lit_list in self._clause_list :
            for lit in lit_list :
                fout.write(' {}'.format(lit))
            fout.write(' 0\n')

        # assumption を単一リテラル節の形で書き出す．
        for lit in assumption_list :
            fout.write(' {} 0\n'.format(lit))
        fout.close()

        # SATソルバを起動する．
        (fh, output_file) = tempfile.mkstemp()
        command_line = [self._satprog, dimacs_file, output_file]
        if self._debug :
            print('SAT program: {}'.format(self._satprog))
            print('INPUT:       {}'.format(dimacs_file))
            print('OUTPUT:      {}'.format(output_file))
            dout = None
            derr = None
        else :
            dout = subprocess.DEVNULL
            derr = subprocess.DEVNULL
        subprocess.run(command_line, stdout = dout, stderr = derr)
        if not self._debug :
            os.remove(dimacs_file)

        # 結果のファイルを読み込む．
        with open(output_file, 'r') as fin :
            lines = fin.readlines()

            # 1行目が結果
            if lines[0] == 'SAT\n' :
                assert len(lines) == 2
                result = SatBool3.B3True
                # 割り当て結果を model に反映させる．
                val_list = lines[1].split()
                model = [SatBool3.B3X for i in range(var_num + 1)]
                for val_str in val_list :
                    val = int(val_str)
                    if val > 0 :
                        model[val] = SatBool3.B3True
                    elif val < 0 :
                        model[-val] = SatBool3.B3False
            elif lines[0] == 'UNSAT\n' :
                result = SatBool3.B3False
        if not self._debug :
            os.remove(output_file)

        return result, model


    ## @brief リテラルが適正な値かチェックする．
    def _check_lit(self, lit) :
        if lit > 0 :
            varid = lit
        elif lit < 0 :
            varid = -lit
        else :
            print('Error in add_clause(), 0 is not allowed as a literal value.')
            return False
        if varid > self._var_count :
            print('Error in add_clause(), {} is out of range'.format(lit))
            return False
        return True
