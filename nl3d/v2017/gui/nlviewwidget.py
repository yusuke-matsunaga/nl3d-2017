#! /usr/bin/env python3

## @file nlviewwidget.py
# @brief NlViewWidget の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2016, 2017 Yusuke Matsunaga
# All rights reserved.

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


## @brief 色と太さを設定したペンを作成する．
def _new_pen(color, width) :
    pen = QPen(color)
    pen.setWidth(width)
    return pen


## @brief ナンバーリンクの１つの層を表すウィジェット
class NlViewWidget(QWidget) :

    # カスタムシグナルの生成
    clicked = pyqtSignal(int, int, QMouseEvent)
    relased = pyqtSignal(int, int, QMouseEvent)
    enter   = pyqtSignal(int, int, QMouseEvent)
    leave   = pyqtSignal(int, int, QMouseEvent)


    ## @brief 初期化
    def __init__(self, parent = None) :

        super(NlViewWidget, self).__init__(parent)

        #
        # スタイルを定義しているパラメータ
        #

        # 周辺部分の幅
        self._FringeSize  = 20
        # マスの大きさ
        self._GridSize    = 50
        # 内枠の幅
        self._InnerMargin = 5
        # 線分の太さ
        self._WireWidth   = 15
        # 端子用のマークの太さ
        self._TermWidth   = 4
        # ビア用のマークの太さ
        self._ViaWidth    = 4
        # 罫線の太さn
        self._LineWidth   = 3
        # フォントサイズ
        self._FontSize    = 16

        # 周辺部分の色
        self._FrameColor  = QColor(180, 150, 100)

        # 盤面の色
        self._BanColor    = QColor(0xB0, 0xB0, 0xB0)

        # 罫線用のペン
        self._LinePen     = _new_pen(QColor(0, 0, 0), self._LineWidth)

        # 線分用のペン
        self._WirePen     = _new_pen(QColor(0, 0, 200), self._WireWidth)

        # 端子用のペン
        self._TermPen     = _new_pen(QColor(50, 50, 150), self._TermWidth)

        # ビア用のペン
        self._ViaPen      = _new_pen(QColor(150, 50, 50), self._ViaWidth)

        # テキスト用のペン
        self._TextPen     = QPen()

        # 数字用のフォント
        self._NumFont = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
        self._NumFont.setBold(True)
        self._NumFont.setPointSize(self._FontSize)

        # フォントメトリックを計算しておく．
        fm = QFontMetrics(self._NumFont)
        self._NumWidth = float(fm.width("99")) * 1.4
        self._NumHeight = float(fm.height()) * 1.4

        self._Width = 0
        self._Height = 0

        self._X0 = 0
        self._Y0 = 0
        self._W = 0
        self._H = 0

        self._StateArray = []
        self._ValArray = []
        self._LabelArray = {}

        self._BanWidth = 0
        self._BanHeight = 0

        self._CurX = -1
        self._CurY = -1

        self._LshapeMode = 3

        self._DrawLine = False

        self._Modified = False

        self.setMouseTracking(True)

        self.set_size(self._Width, self._Height)


    ## @brief クリアする．
    def clear(self) :
        for x in range(0, self._Width) :
            for y in range(0, self._Height) :
                index = self.xy_to_index(x, y)
                self._StateArray[index] = 0
                self._ValArray[index] = 0
        self._LabelArray = {}
        self._Modified = False


    ## @brief 盤面のサイズを設定する．
    # @param[in] width 幅
    # @param[in] height 高さ
    #
    # 以前の内容はクリアされる．
    def set_size(self, width, height) :
        self.clear()

        self._Width = width
        self._Height = height

        self._BanWidth = width * self._GridSize + self._FringeSize + self._NumWidth
        self._BanHeight = height * self._GridSize + self._FringeSize + self._NumHeight

        n = width * height
        self._ValArray = [0 for i in range(0, n)]
        self._StateArray = [0 for i in range(0, n)]


    ## @brief 指定されたマスが端子の時に True を返す．
    # @param[in] x, y 座標
    def is_terminal(self, x, y) :
        index = self.xy_to_index(x, y)
        if self._StateArray[index] & 1 :
            return True
        else :
            return False


    ## @brief 指定されたマスがビアの時に True を返す．
    # @param[in] x, y 座標
    def is_via(self, x, y) :
        index = self.xy_to_index(x, y)
        if self._StateArray[index] & 2 :
            return True
        else :
            return False


    ## @brief 指定されたマスの線分番号を返す．
    # @param[in] x, y 座標
    def grid_val(self, x, y) :
        index = self.xy_to_index(x, y)
        return self._ValArray[index]


    ## @brief 指定されたマスのビア番号を返す．
    # @param[in] x, y 座標
    #
    # 指定されたマスがビアでないときの値は不定
    def via_label(self, x, y) :
        assert self.is_via(x, y)
        index = self.xy_to_index(x, y)
        via_id = self._StateArray[index] >> 2
        return self._LabelArray[via_id]


    ## @brief 変更フラグをクリアする．
    def clear_modified(self) :
        self._Modified = False


    ## @brief 変更フラグを得る．
    def is_modified(self) :
        return self._Modified


    ## @brief サイズヒントを返す．
    def sizeHint(self) :
        return QSize(self._BanWidth, self._BanHeight)


    ## @brief 終端の設定をする．
    # @param[in] x, y 座標
    # @param[in] val 線分番号
    def set_terminal(self, x, y, val) :
        assert x < self._Width
        assert y < self._Height
        index = self.xy_to_index(x, y)
        self._StateArray[index] |= 1
        self.set_val(x, y, val)


    ## @brief ビアの設定をする．
    # @param[in] via_id ビア番号
    # @param[in] x, y 座標
    # @param[in] label ラベル
    def set_via(self, via_id, x, y, label) :
        assert x < self._Width
        assert y < self._Height
        index = self.xy_to_index(x, y)
        self._StateArray[index] |= 2
        self._StateArray[index] |= (via_id << 2)
        self._LabelArray[via_id] = label


    ## @brief 線分番号を設定する．
    # @param[in] x, y 座標
    # @param[in] val 線分番号
    def set_val(self, x, y, val) :
        assert x < self._Width
        assert y < self._Height
        index = self.xy_to_index(x, y)
        self._ValArray[index] = val
        self._Modified = True

        self.update()


    ## @brief 解の線分を描画するようにする．
    def set_solution_mode(self) :
        self._DrawLine = True


    ## @brief paint イベント
    # @param[in] event イベント構造体
    def paintEvent(self, event) :

        # ウインドウサイズの縦横比と盤面の縦横比が異なる時の補正
        w = self.width()
        h = self.height()

        w1_f = (self._BanWidth * h) / float(self._BanHeight)
        h1_f = (self._BanHeight * w) / float(self._BanWidth)
        w1 = int(w1_f)
        h1 = int(h1_f)

        if w1 > w :
            assert h1 <= h
            self._X0 = 0
            self._Y0 = (h - h1) / 2
            self._W = w
            self._H = h1
        else :
            self._X0 = (w - w1) / 2
            self._Y0 = 0
            self._W = w1
            self._H = h

        # ペインタの生成
        painter = QPainter(self)

        painter.setWindow(0, 0, self._BanWidth, self._BanHeight)
        painter.setViewport(self._X0, self._Y0, self._W, self._H)
        painter.setFont(self._NumFont)

        # 外枠の描画
        painter.fillRect(0, 0, self._BanWidth, self._BanHeight, self._FrameColor)

        # 盤
        painter.fillRect(self._NumWidth, self._NumHeight,
                         self._BanWidth - self._FringeSize - self._NumWidth,
                         self._BanHeight - self._FringeSize - self._NumHeight,
                         self._BanColor)

        # 目盛り
        painter.save()
        painter.setPen(self._TextPen)
        for i in range(0, self._Width) :
            x0 = i * self._GridSize + self._NumWidth
            y0 = 0
            buff = '{:2d}'.format(i)
            painter.drawText(QRect(x0, y0, self._GridSize, self._NumHeight),
                             Qt.AlignCenter, buff)
        for i in range(0, self._Height) :
            x0 = 0
            y0 = i * self._GridSize + self._NumHeight
            buff = '{:2d}'.format(i)
            painter.drawText(QRect(x0, y0, self._NumWidth, self._GridSize),
                             Qt.AlignCenter, buff)
        painter.restore()

        # 区切り線
        painter.save()
        painter.setPen(self._LinePen)
        for i in range(0, self._Height) :
            x0, y0 = self.xy_to_local(0, i)
            x1, y1 = self.xy_to_local(self._Width, i)
            painter.drawLine(x0, y0, x1, y1)
        for i in range(0, self._Width) :
            x0, y0 = self.xy_to_local(i, 0)
            x1, y1 = self.xy_to_local(i, self._Height)
            painter.drawLine(x0, y0, x1, y1)
        painter.restore()

        # 端点とビアの描画
        painter.save()

        for x in range(0, self._Width) :
            for y in range(0, self._Height) :
                if self.is_terminal(x, y) :
                    x0, y0 = self.xy_to_local(x, y)
                    painter.setPen(self._TermPen)
                    painter.drawRect(x0 + self._InnerMargin, y0 + self._InnerMargin,
                                     self._GridSize - self._InnerMargin * 2,
                                     self._GridSize - self._InnerMargin * 2)
                    index = self.xy_to_index(x, y)
                    val = self._ValArray[index]
                    if val < 10 :
                        buff = '{:1d}'.format(val)
                    else :
                        buff = '{:2d}'.format(val)
                    painter.setPen(self._TextPen)
                    painter.drawText(QRect(x0, y0, self._GridSize, self._GridSize),
                                     Qt.AlignCenter, buff)
                elif self.is_via(x, y) :
                    x0, y0 = self.xy_to_local(x, y)
                    painter.setPen(self._ViaPen)
                    painter.drawRect(x0 + self._InnerMargin, y0 + self._InnerMargin,
                                     self._GridSize - self._InnerMargin * 2,
                                     self._GridSize - self._InnerMargin * 2)
                    label = self.via_label(x, y)
                    painter.setPen(self._TextPen)
                    painter.drawText(QRect(x0, y0, self._GridSize, self._GridSize),
                                     Qt.AlignCenter, label)
        painter.restore()

        if not self._DrawLine :
            return

        # 水平方向の結線の描画
        painter.save()
        painter.setPen(self._WirePen)
        for x in range(0, self._Width - 1) :
            for y in range(0, self._Height) :
                val0 = self._ValArray[self.xy_to_index(x, y)]
                val1 = self._ValArray[self.xy_to_index(x + 1, y)]

                if val0 != val1 or val0 == 0 :
                    continue

                x0, y0 = self.xy_to_local(x, y)
                cx0 = x0 + self._GridSize / 2
                cx1 = cx0 + self._GridSize
                cy  = y0 + self._GridSize / 2

                if self.is_terminal(x, y) or self.is_via(x, y) :
                    cx0 = x0 + self._GridSize - self._InnerMargin + self._WireWidth / 2
                if self.is_terminal(x + 1, y) or self.is_via(x + 1, y) :
                    cx1 = x0 + self._GridSize + self._InnerMargin - self._WireWidth / 2

                painter.drawLine(cx0, cy, cx1, cy)
        painter.restore()

        # 垂直方向の結線の描画
        painter.save()
        painter.setPen(self._WirePen)
        for y in range(0, self._Height - 1) :
            for x in range(0, self._Width) :
                val0 = self._ValArray[self.xy_to_index(x, y)]
                val1 = self._ValArray[self.xy_to_index(x, y + 1)]

                if val0 != val1 or val0 == 0 :
                    continue

                x0, y0 = self.xy_to_local(x, y)
                cx  = x0 + self._GridSize / 2
                cy0 = y0 + self._GridSize / 2
                cy1 = cy0 + self._GridSize

                if self.is_terminal(x, y) or self.is_via(x, y) :
                    cy0 = y0 + self._GridSize - self._InnerMargin + self._WireWidth / 2
                if self.is_terminal(x, y + 1) or self.is_via(x, y + 1) :
                    cy1 = y0 + self._GridSize + self._InnerMargin - self._WireWidth / 2

                painter.drawLine(cx, cy0, cx, cy1)
        painter.restore()


    ## @brief Button Press イベント
    # @param[in] event イベント構造体
    def mousePressEvent(self, event) :
        ret, x, y = self.get_xy(event)
        if ret :
            self.clicked.emit(x, y, event)


    ## @brief Button Release イベント
    # @param[in] event イベント構造体
    def mouseRelaseEvent(self, event) :
        ret, x, y = self.get_xy(event)
        if ret :
            self.released.emit(x, y, event)


    ## @brief Motion notify イベント
    # @param[in] event イベント構造体
    def mouseMoveEvent(self, event) :
        ret, x, y = self.get_xy(event)
        if ret :
            if x != self._CurX or y != self._CurY :
                if self._CurX >= 0 and self._CurY >= 0 :
                    self.leave.emit(self._CurX, self._CurY, event)
                self._CurX = x
                self._CurY = y
                self.enter.emit(self._CurX, self._CurY, event)
            else :
                if self._CurX >= 0 and self._CurY >= 0 :
                    self.leave.emit(self._CurX, self._CurY, event)
                self._CurX = -1
                self._CurY = -1


    ## @brief マウスの座標から格子座標を得る．
    # @param[in] event イベント構造体
    # @retval (x, y) 格子座標
    # @retval None 格子内に入っていなかった時
    def get_xy(self, event) :
        gx = event.x() - self._X0
        gy = event.y() - self._Y0

        if gx < 0 or gx > self._W :
            return False, 0, 0
        if gy < 0 or gy > self._H :
            return False, 0, 0

        lx = float(gx) * self._BanWidth / self._W
        ly = float(gy) * self._BanHeight / self._H

        if lx < self._NumWidth or lx >= (self._BanWidth - self._FringeSize) :
            return False, 0, 0

        if ly < self._NumHeight or ly >= (self._BanHeight - self._FringeSize) :
            return False, 0, 0

        x = int((lx - self._NumWidth) / self._GridSize)
        y = int((ly - self._NumHeight) / self._GridSize)

        return True, x, y


    ## @brief 格子座標からローカル座標を得る．
    # @param[in] x, y 格子座標
    # @return ローカル座標
    def xy_to_local(self, x, y) :
        lx = x * self._GridSize + self._NumWidth
        ly = y * self._GridSize + self._NumHeight
        return lx, ly


    ## @brief 格子座標からインデックスを得る．
    # @param[in] x, y 格子座標
    # @return インデックス
    def xy_to_index(self, x, y) :
        assert x >= 0 and x < self._Width
        assert y >= 0 and y < self._Height
        return x * self._Height + y


    ## @brief インデックスから格子座標を得る．
    # @param[in] index インデックス
    # @return 格子座標
    def index_to_xy(self, index) :
        assert index >= 0 and index < (self._Width * self._Height)
        x = index // self._Height
        y = index % self._Height
        return x, y
