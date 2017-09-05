#! /usr/bin/env python3

### @file gui/viewwidget.py
### @brief ViewWidget の定義ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2016, 2017 Yusuke Matsunaga
### All rights reserved.

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


### @brief 色と太さを設定したペンを作成する．
def new_pen(color, width) :
    pen = QPen(color)
    pen.setWidth(width)
    return pen


### @brief ナンバーリンクの１つの層を表すウィジェット
class ViewWidget(QWidget) :

    # カスタムシグナルの生成
    clicked = pyqtSignal(int, int, QMouseEvent)
    relased = pyqtSignal(int, int, QMouseEvent)
    enter   = pyqtSignal(int, int, QMouseEvent)
    leave   = pyqtSignal(int, int, QMouseEvent)


    ### @brief 初期化
    def __init__(self, parent = None) :

        super(ViewWidget, self).__init__(parent)

        #
        # スタイルを定義しているパラメータ
        #

        # 周辺部分の幅
        self.__FringeSize  = 20
        # マスの大きさ
        self.__GridSize    = 50
        # 内枠の幅
        self.__InnerMargin = 5
        # 線分の太さ
        self.__WireWidth   = 15
        # 端子用のマークの太さ
        self.__TermWidth   = 4
        # ビア用のマークの太さ
        self.__ViaWidth    = 4
        # 罫線の太さn
        self.__LineWidth   = 3
        # フォントサイズ
        self.__FontSize    = 16

        # 周辺部分の色
        self.__FrameColor  = QColor(180, 150, 100)

        # 盤面の色
        self.__BanColor    = QColor(0xB0, 0xB0, 0xB0)

        # 罫線用のペン
        self.__LinePen     = new_pen(QColor(0, 0, 0), self.__LineWidth)

        # 線分用のペン
        self.__WirePen     = new_pen(QColor(0, 0, 200), self.__WireWidth)

        # 端子用のペン
        self.__TermPen     = new_pen(QColor(50, 50, 150), self.__TermWidth)

        # ビア用のペン
        self.__ViaPen      = new_pen(QColor(150, 50, 50), self.__ViaWidth)

        # テキスト用のペン
        self.__TextPen     = QPen()

        # 数字用のフォント
        self.__NumFont = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
        self.__NumFont.setBold(True)
        self.__NumFont.setPointSize(self.__FontSize)

        # フォントメトリックを計算しておく．
        fm = QFontMetrics(self.__NumFont)
        self.__NumWidth = float(fm.width("99")) * 1.4
        self.__NumHeight = float(fm.height()) * 1.4

        self.__Width = 0
        self.__Height = 0

        self.__X0 = 0
        self.__Y0 = 0
        self.__W = 0
        self.__H = 0

        self.__StateArray = []
        self.__ValArray = []
        self.__LabelArray = {}

        self.__BanWidth = 0
        self.__BanHeight = 0

        self.__CurX = -1
        self.__CurY = -1

        self.__LshapeMode = 3

        self.__DrawLine = False

        self.__Modified = False

        self.setMouseTracking(True)

        self.set_size(self.__Width, self.__Height)


    ### @brief クリアする．
    def clear(self) :
        for x in range(0, self.__Width) :
            for y in range(0, self.__Height) :
                index = self.xy_to_index(x, y)
                self.__StateArray[index] = 0
                self.__ValArray[index] = 0
        self.__LabelArray = {}
        self.__Modified = False


    ### @brief 盤面のサイズを設定する．
    ### @param[in] width 幅
    ### @param[in] height 高さ
    ###
    ### 以前の内容はクリアされる．
    def set_size(self, width, height) :
        self.clear()

        self.__Width = width
        self.__Height = height

        self.__BanWidth = width * self.__GridSize + self.__FringeSize + self.__NumWidth
        self.__BanHeight = height * self.__GridSize + self.__FringeSize + self.__NumHeight

        n = width * height
        self.__ValArray = [0 for i in range(0, n)]
        self.__StateArray = [0 for i in range(0, n)]


    ### @brief 指定されたマスが端子の時に True を返す．
    ### @param[in] x, y 座標
    def is_terminal(self, x, y) :
        index = self.xy_to_index(x, y)
        if self.__StateArray[index] & 1 :
            return True
        else :
            return False


    ### @brief 指定されたマスがビアの時に True を返す．
    ### @param[in] x, y 座標
    def is_via(self, x, y) :
        index = self.xy_to_index(x, y)
        if self.__StateArray[index] & 2 :
            return True
        else :
            return False


    ### @brief 指定されたマスの線分番号を返す．
    ### @param[in] x, y 座標
    def grid_val(self, x, y) :
        index = self.xy_to_index(x, y)
        return self.__ValArray[index]


    ### @brief 指定されたマスのビア番号を返す．
    ### @param[in] x, y 座標
    ###
    ### 指定されたマスがビアでないときの値は不定
    def via_label(self, x, y) :
        assert self.is_via(x, y)
        index = self.xy_to_index(x, y)
        via_id = self.__StateArray[index] >> 2
        return self.__LabelArray[via_id]


    ### @brief 変更フラグをクリアする．
    def clear_modified(self) :
        self._Modified = False


    ### @brief 変更フラグを得る．
    def is_modified(self) :
        return self.__Modified


    ### @brief サイズヒントを返す．
    def sizeHint(self) :
        return QSize(self.__BanWidth, self.__BanHeight)


    ### @brief 終端の設定をする．
    ### @param[in] x, y 座標
    ### @param[in] val 線分番号
    def set_terminal(self, x, y, val) :
        assert 0 <= x < self.__Width
        assert 0 <= y < self.__Height
        index = self.xy_to_index(x, y)
        self.__StateArray[index] |= 1
        self.set_val(x, y, val)


    ### @brief ビアの設定をする．
    ### @param[in] via_id ビア番号
    ### @param[in] x, y 座標
    ### @param[in] label ラベル
    def set_via(self, via_id, x, y, label) :
        assert 0 <= x < self.__Width
        assert 0 <= y < self.__Height
        index = self.xy_to_index(x, y)
        self.__StateArray[index] |= 2
        self.__StateArray[index] |= (via_id << 2)
        self.__LabelArray[via_id] = label


    ### @brief 線分番号を設定する．
    ### @param[in] x, y 座標
    ### @param[in] val 線分番号
    def set_val(self, x, y, val) :
        assert 0 <= x < self.__Width
        assert 0 <= y < self.__Height
        index = self.xy_to_index(x, y)
        self.__ValArray[index] = val
        self.__Modified = True

        self.update()


    ### @brief 解の線分を描画するようにする．
    def set_solution_mode(self) :
        self.__DrawLine = True


    ### @brief paint イベント
    ### @param[in] event イベント構造体
    def paintEvent(self, event) :

        # ウインドウサイズの縦横比と盤面の縦横比が異なる時の補正
        w = self.width()
        h = self.height()

        w1_f = (self.__BanWidth * h) / float(self.__BanHeight)
        h1_f = (self.__BanHeight * w) / float(self.__BanWidth)
        w1 = int(w1_f)
        h1 = int(h1_f)

        if w1 > w :
            assert h1 <= h
            self.__X0 = 0
            self.__Y0 = (h - h1) / 2
            self.__W = w
            self.__H = h1
        else :
            self.__X0 = (w - w1) / 2
            self.__Y0 = 0
            self.__W = w1
            self.__H = h

        # ペインタの生成
        painter = QPainter(self)

        painter.setWindow(0, 0, self.__BanWidth, self.__BanHeight)
        painter.setViewport(self.__X0, self.__Y0, self.__W, self.__H)
        painter.setFont(self.__NumFont)

        # 外枠の描画
        painter.fillRect(0, 0, self.__BanWidth, self.__BanHeight, self.__FrameColor)

        # 盤
        painter.fillRect(self.__NumWidth, self.__NumHeight,
                         self.__BanWidth - self.__FringeSize - self.__NumWidth,
                         self.__BanHeight - self.__FringeSize - self.__NumHeight,
                         self.__BanColor)

        # 目盛り
        painter.save()
        painter.setPen(self.__TextPen)
        for i in range(0, self.__Width) :
            x0 = i * self.__GridSize + self.__NumWidth
            y0 = 0
            buff = '{:2d}'.format(i)
            painter.drawText(QRect(x0, y0, self.__GridSize, self.__NumHeight),
                             Qt.AlignCenter, buff)
        for i in range(0, self.__Height) :
            x0 = 0
            y0 = i * self.__GridSize + self.__NumHeight
            buff = '{:2d}'.format(i)
            painter.drawText(QRect(x0, y0, self.__NumWidth, self.__GridSize),
                             Qt.AlignCenter, buff)
        painter.restore()

        # 区切り線
        painter.save()
        painter.setPen(self.__LinePen)
        for i in range(0, self.__Height) :
            x0, y0 = self.xy_to_local(0, i)
            x1, y1 = self.xy_to_local(self.__Width, i)
            painter.drawLine(x0, y0, x1, y1)
        for i in range(0, self.__Width) :
            x0, y0 = self.xy_to_local(i, 0)
            x1, y1 = self.xy_to_local(i, self.__Height)
            painter.drawLine(x0, y0, x1, y1)
        painter.restore()

        # 端点とビアの描画
        painter.save()

        for x in range(0, self.__Width) :
            for y in range(0, self.__Height) :
                if self.is_terminal(x, y) :
                    x0, y0 = self.xy_to_local(x, y)
                    painter.setPen(self.__TermPen)
                    painter.drawRect(x0 + self.__InnerMargin, y0 + self.__InnerMargin,
                                     self.__GridSize - self.__InnerMargin * 2,
                                     self.__GridSize - self.__InnerMargin * 2)
                    index = self.xy_to_index(x, y)
                    val = self.__ValArray[index]
                    if val < 10 :
                        buff = '{:1d}'.format(val)
                    else :
                        buff = '{:2d}'.format(val)
                    painter.setPen(self.__TextPen)
                    painter.drawText(QRect(x0, y0, self.__GridSize, self.__GridSize),
                                     Qt.AlignCenter, buff)
                elif self.is_via(x, y) :
                    x0, y0 = self.xy_to_local(x, y)
                    painter.setPen(self.__ViaPen)
                    painter.drawRect(x0 + self.__InnerMargin, y0 + self.__InnerMargin,
                                     self.__GridSize - self.__InnerMargin * 2,
                                     self.__GridSize - self.__InnerMargin * 2)
                    label = self.via_label(x, y)
                    painter.setPen(self.__TextPen)
                    painter.drawText(QRect(x0, y0, self.__GridSize, self.__GridSize),
                                     Qt.AlignCenter, label)
        painter.restore()

        if not self.__DrawLine :
            return

        # 水平方向の結線の描画
        painter.save()
        painter.setPen(self.__WirePen)
        for x in range(0, self.__Width - 1) :
            for y in range(0, self.__Height) :
                val0 = self.__ValArray[self.xy_to_index(x, y)]
                val1 = self.__ValArray[self.xy_to_index(x + 1, y)]

                if val0 != val1 or val0 == 0 :
                    continue

                x0, y0 = self.xy_to_local(x, y)
                cx0 = x0 + self.__GridSize / 2
                cx1 = cx0 + self.__GridSize
                cy  = y0 + self.__GridSize / 2

                if self.is_terminal(x, y) or self.is_via(x, y) :
                    cx0 = x0 + self.__GridSize - self.__InnerMargin + self.__WireWidth / 2
                if self.is_terminal(x + 1, y) or self.is_via(x + 1, y) :
                    cx1 = x0 + self.__GridSize + self.__InnerMargin - self.__WireWidth / 2

                painter.drawLine(cx0, cy, cx1, cy)
        painter.restore()

        # 垂直方向の結線の描画
        painter.save()
        painter.setPen(self.__WirePen)
        for y in range(0, self.__Height - 1) :
            for x in range(0, self.__Width) :
                val0 = self.__ValArray[self.xy_to_index(x, y)]
                val1 = self.__ValArray[self.xy_to_index(x, y + 1)]

                if val0 != val1 or val0 == 0 :
                    continue

                x0, y0 = self.xy_to_local(x, y)
                cx  = x0 + self.__GridSize / 2
                cy0 = y0 + self.__GridSize / 2
                cy1 = cy0 + self.__GridSize

                if self.is_terminal(x, y) or self.is_via(x, y) :
                    cy0 = y0 + self.__GridSize - self.__InnerMargin + self.__WireWidth / 2
                if self.is_terminal(x, y + 1) or self.is_via(x, y + 1) :
                    cy1 = y0 + self.__GridSize + self.__InnerMargin - self.__WireWidth / 2

                painter.drawLine(cx, cy0, cx, cy1)
        painter.restore()


    ### @brief Button Press イベント
    ### @param[in] event イベント構造体
    def mousePressEvent(self, event) :
        ret, x, y = self.get_xy(event)
        if ret :
            self.clicked.emit(x, y, event)


    ### @brief Button Release イベント
    ### @param[in] event イベント構造体
    def mouseRelaseEvent(self, event) :
        ret, x, y = self.get_xy(event)
        if ret :
            self.released.emit(x, y, event)


    ### @brief Motion notify イベント
    ### @param[in] event イベント構造体
    def mouseMoveEvent(self, event) :
        ret, x, y = self.get_xy(event)
        if ret :
            if x != self.__CurX or y != self.__CurY :
                if self.__CurX >= 0 and self.__CurY >= 0 :
                    self.leave.emit(self.__CurX, self.__CurY, event)
                self.__CurX = x
                self.__CurY = y
                self.enter.emit(self.__CurX, self.__CurY, event)
            else :
                if self.__CurX >= 0 and self.__CurY >= 0 :
                    self.leave.emit(self.__CurX, self.__CurY, event)
                self.__CurX = -1
                self.__CurY = -1


    ### @brief マウスの座標から格子座標を得る．
    ### @param[in] event イベント構造体
    ### @retval (x, y) 格子座標
    ### @retval None 格子内に入っていなかった時
    def get_xy(self, event) :
        gx = event.x() - self.__X0
        gy = event.y() - self.__Y0

        if gx < 0 or gx > self.__W :
            return False, 0, 0
        if gy < 0 or gy > self.__H :
            return False, 0, 0

        lx = float(gx) * self.__BanWidth / self.__W
        ly = float(gy) * self.__BanHeight / self.__H

        if lx < self.__NumWidth or lx >= (self.__BanWidth - self.__FringeSize) :
            return False, 0, 0

        if ly < self.__NumHeight or ly >= (self.__BanHeight - self.__FringeSize) :
            return False, 0, 0

        x = int((lx - self.__NumWidth) / self.__GridSize)
        y = int((ly - self.__NumHeight) / self.__GridSize)

        return True, x, y


    ### @brief 格子座標からローカル座標を得る．
    ### @param[in] x, y 格子座標
    ### @return ローカル座標
    def xy_to_local(self, x, y) :
        lx = x * self.__GridSize + self.__NumWidth
        ly = y * self.__GridSize + self.__NumHeight
        return lx, ly


    ### @brief 格子座標からインデックスを得る．
    ### @param[in] x, y 格子座標
    ### @return インデックス
    def xy_to_index(self, x, y) :
        assert x >= 0 and x < self.__Width
        assert y >= 0 and y < self.__Height
        return x * self.__Height + y


    ### @brief インデックスから格子座標を得る．
    ### @param[in] index インデックス
    ### @return 格子座標
    def index_to_xy(self, index) :
        assert index >= 0 and index < (self.__Width * self.__Height)
        x = index // self.__Height
        y = index % self.__Height
        return x, y
