# This Python file uses the following encoding: utf-8
import sys
import os
import random

from PySide2.QtGui import QGuiApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QObject, Slot, QUrl


Columns = 12
Rows = 20
SHAPES = [
            [],
            [(-1, -1), (0, -1), (-1, 0), (0, 0)],
            [(-1, 0), (0, 0), (0, -1), (1, -1)],
            [(-1, 0), (0, 0), (0, -1), (1, 0)],
            [(0, 1), (0, 0), (0, -1), (0, -2)],
            [(-1, 0), (0, 0), (-1, -1), (-1, -2)],
            [(-1, 0), (0, 0), (0, -1), (0, -2)],
            [(-1, -1), (0, -1), (0, 0), (1, 0)]
]
NoShape = 0


class TetrixPiece():
    '随机生成俄罗斯方块，并随机旋转几次'

    def __init__(self, shape, rotatetimes=0):
        self.shape = shape
        self.cell_list = SHAPES[self.shape]
        if rotatetimes > 0:
            for i in range(rotatetimes):
                self.rotate_left()

    def rotate_left(self):
        rotate_cell_list = []
        for cell in self.cell_list:
            cc, cr = cell
            rotate_cell_list.append((cr, -cc))
        self.cell_list = rotate_cell_list

    def rotate_right(self):
        rotate_cell_list = []
        for cell in self.cell_list:
            cc, cr = cell
            rotate_cell_list.append((-cr, cc))
        self.cell_list = rotate_cell_list

    def getleft(self):
        return min([cr[0] for cr in self.cell_list])

    def getright(self):
        return max([cr[0] for cr in self.cell_list])

    def gettop(self):
        return min([cr[1] for cr in self.cell_list])

    def getbottom(self):
        return max([cr[1] for cr in self.cell_list])

    def getnextPieceXoffset(self):
        width = (self.getright()-self.getleft())
        return (6-width)/2-self.getleft()

    def getnextPieceYoffset(self):
        height = (self.getbottom()-self.gettop())
        return (6-height)/2-self.gettop()


class TetrixBoard(QObject):
    def __init__(self):  # 构造函数
        super().__init__()  # 一定要调用父类的构造函数
        self.table = []
        self.newGame()

    def CR2Index(self, cr):
        return cr[0]+cr[1]*Columns

    def Index2CR(self, index):
        return (index % Columns, index // Columns)

    def check_row_full(self, r):
        '检查第r行是否满了'

        for i in range(r*Columns, (r+1)*Columns):
            if self.table[i] == NoShape:
                return False
        return True

    @Slot(int, result=int)  # 修饰器，供QML文件调用
    def getShapeAt(self, i):
        '得到某个位置的形状，供QML中用对应颜色填充'
        return self.table[i]

    def setShapeAt(self, cr, shape):
        c, r = cr
        self.table[r*Columns+c] = shape

    def check_and_clear(self):
        fulllines = 0
        for ri in range(Rows):
            if self.check_row_full(ri):
                fulllines += 1
                for r in range(ri, 1, -1):
                    for c in range(Columns):
                        self.table[r*Columns+c] = self.table[(r-1)*Columns + c]
                for j in range(Columns):
                    self.table[j] = NoShape
        s = (fulllines + 1) * fulllines * 5
        self.score += s   # 一次消除的行越多，加分越多

    def clearboard(self):  # 清空板子
        self.table = [NoShape for i in range(Rows * Columns)]

    @Slot(int, result=int)
    def getCurPieceIndex(self, i):
        '得到当前第i个块在表中的位置'
        if self.curPiece is None:
            return 0
        else:
            c0, r0 = self.curPiece.cell_list[i]
            c1, r1 = self.curCR
            index = (c0+c1)+(r0+r1)*Columns
            #  print("getCurPieceIndex:", index)
            return index

    @Slot(result=list)
    def getCR(self):
        return self.curCR

    @Slot(int, result=int)
    def getnextPieceX(self, index):
        '得到下一个块中第index个的列位置，供提示区中显示出来'
        Xoffset = self.nextPiece.getnextPieceXoffset()
        cell = self.nextPiece.cell_list[index]
        return cell[0] + Xoffset

    @Slot(int, result=int)
    def getnextPieceY(self, index):
        '得到下一个块中第index个的行位置，供提示区中显示出来'
        Yoffset = self.nextPiece.getnextPieceYoffset()
        cell = self.nextPiece.cell_list[index]
        return cell[1] + Yoffset

    @Slot(result=int)
    def getScore(self):
        return self.score

    @Slot(result=int)
    def getShape(self):
        if self.curPiece is None:
            return NoShape
        else:
            return self.curPiece.shape

    @Slot(result=int)
    def getNextShape(self):
        if self.nextPiece is None:
            return NoShape
        else:
            return self.nextPiece.shape

    @Slot()
    def newGame(self):
        self.clearboard()
        self.curPiece = None
        self.nextPiece = None
        self.isWaitingNextPiece = True
        self.score = 0
        self.curCR = (Columns//2, 0)
        self.newPiece()

    @Slot()
    def left(self):
        if self.try_move((-1, 0)):   # 如果能够向左移动一格
            self.move((-1, 0))       # 就移动一格

    @Slot()
    def right(self):
        if self.try_move((1, 0)):    # 如果能够向右移动一格
            self.move((1, 0))        # 就移动一格

    @Slot()
    def down(self):
        if self.try_move((0, 1)):    # 如果能够向下移动一格
            self.move((0, 1))        # 就向下移动一格

    @Slot()
    def rotateLeft(self):
        self.curPiece.rotate_left()     # 向左转动
        if self.try_move([0, 0]) is False:  # 如果检查不能转动
            self.curPiece.rotate_right()   # 再转回来

    @Slot()
    def rotateRight(self):
        self.curPiece.rotate_right()    # 向右转动
        if self.try_move([0, 0]) is False:  # 如果不能转动
            self.curPiece.rotate_left()    # 再转回来

    @Slot()
    def land(self):     # 到底
        max_down = 0    # 最大向下的数量
        for i in range(Rows):
            if self.try_move([0, i]) is True:
                max_down = i
            else:
                break
        self.move([0, max_down])
        #  self.oneLineDown()
        self.save_block_to_table()
        self.isWaitingNextPiece = True   # 表示开始下一个
        self.curPiece = None
        self.check_and_clear()  # 检查表里是否满行了

    def newPiece(self):
        nextshape = random.randint(1, 7)
        rotatetimes = random.randint(0, 3)
        self.nextPiece = TetrixPiece(nextshape, rotatetimes)

    @Slot()
    def timerEvent(self):
        if self.isWaitingNextPiece:  # 如果在等下一个
            self.isWaitingNextPiece = False
            self.curPiece = self.nextPiece
            self.curCR = [Columns//2, 0]

            if not self.try_move((0, 1)):  # 如果新的curPiece不能移动，说明gameover了
                self.gameover()
                return
            else:
                self.newPiece()
        else:   # 如果不是在等下一个
            self.oneLineDown()

    def gameover(self):
        pass

    def oneLineDown(self):
        if self.try_move((0, 1)):    # 如果能够向下移动一行
            self.move((0, 1))        # 向下移动一行
        else:                       # 否则就是到底了
            self.save_block_to_table()
            self.isWaitingNextPiece = True   # 表示开始下一个
            self.curPiece = None

            self.check_and_clear()  # 检查表里是否满行了

    def move(self, direction=[0, 0]):
        "绘制向指定方向移动后的俄罗斯方块"
        self.curCR[0] += direction[0]
        self.curCR[1] += direction[1]

    def try_move(self, direction=[0, 0]):
        """
            判断俄罗斯方块是否可以朝指定方向移动
            :param direction: 俄罗斯方块移动方向
            :return: boolean 是否可以朝指定方向移动
        """
        c1, r1 = self.curCR
        dc, dr = direction

        for cell in self.curPiece.cell_list:
            cell_c, cell_r = cell
            c = cell_c + c1 + dc
            r = cell_r + r1 + dr
            index = self.CR2Index((c, r))
            # 判断该位置是否超出左右边界，以及下边界
            # 一般不判断上边界，因为俄罗斯方块生成的时候，可能有一部分在上边界之上还没有出来
            if c < 0 or c >= Columns or r >= Rows:
                return False
            # 必须要判断r不小于0才行，具体原因你可以不加这个判断，试试会出现什么效果
            if(r >= 0):
                if(self.getShapeAt(index) != 0):
                    return False
        return True

    def save_block_to_table(self):
        for cell in self.curPiece.cell_list:
            c0, r0 = cell
            c = self.curCR[0]+c0
            r = self.curCR[1]+r0
            self.setShapeAt((c, r), self.curPiece.shape)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    #  Expose the list to the Qml code
    random.seed(None)
    tetrix = TetrixBoard()

    context = view.rootContext()
    context.setContextProperty("tetrix", tetrix)

    #  Load the QML file
    qml_file = os.path.join(os.path.dirname(__file__), "view.qml")
    view.setSource(QUrl.fromLocalFile(os.path.abspath(qml_file)))

    #  Show the window
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()

    #  execute and cleanup
    app.exec_()
    del view
