from copy import copy
import json


def getConfig(fileinput):
    with open(fileinput, 'r', encoding='utf-8') as file:
        data = file.read()
    obj = json.loads(data)
    return obj


# copy sang phai 
#rowStart dòng bắt đầu
#rowEnd dòng kết thúc
# cột bẮT đầu
# leng: độ rộng
# num: số lần

def insertAndCopyColumns(ws, rowStart, rowEnd, colStart, leng, num):
    rangeSelected = []
    for i in range(rowStart, rowEnd + 1):
        rowSelected = []
        for j in range(colStart, colStart + leng):
            rowSelected.append(ws.cell(row = i, column = j).value)
        rangeSelected.append(rowSelected)
    countRow = 0
    for i in range(rowStart, rowEnd + 1):
        countCol = 0
        for j in range(colStart + (leng * num), colStart + (leng * num) + leng):
            ws.cell(row = i, column = j).value = rangeSelected[countRow][countCol]
            ws.cell(row = i, column = j)._style = copy(ws.cell(row = i, column = j - leng)._style)
            countCol += 1
        countRow += 1


def insertAndCopyRowsWithNo(ws, rowStart, colStart, colEnd, leng, no):
    rangeSelected = []
    for i in range(rowStart, rowStart + leng):
        rowSelected = []
        for j in range(colStart, colEnd):
            rowSelected.append(ws.cell(row = i, column = j).value)
        rangeSelected.append(rowSelected)

    countRow = 0
    for i in range(rowStart + leng, rowStart + leng * 2):
        countCol = 0
        for j in range(colStart , colEnd):
            if rangeSelected[0][1] == 'ブロックデバイスの詳細 1':
                rangeSelected[0][1] = 'ブロックデバイスの詳細 ' + str(no)
            ws.cell(row = i, column = j).value = rangeSelected[countRow][countCol]
            ws.cell(row = i, column = j)._style = copy(ws.cell(row = i - leng, column = j)._style)
            countCol += 1
        countRow += 1

#copy x
def insertAndCopyRows(ws, rowStart, colStart, colEnd, leng):
    rangeSelected = []
    for i in range(rowStart, rowStart + leng):
        rowSelected = []
        for j in range(colStart, colEnd):
            rowSelected.append(ws.cell(row = i, column = j).value)
        rangeSelected.append(rowSelected)

    countRow = 0
    for i in range(rowStart + leng, rowStart + leng * 2):
        countCol = 0
        for j in range(colStart , colEnd):
            ws.cell(row = i, column = j).value = rangeSelected[countRow][countCol]
            ws.cell(row = i, column = j)._style = copy(ws.cell(row = i - leng, column = j)._style)
            countCol += 1
        countRow += 1

#insert uong dưới 
#maxInput: số lần
#rowRange: độ rộng
#rowInsert: bắtđầu bên dưới
def insertAndCopyRowRange(ws, maxInput, rowRange, rowInsert):
    for i in range(1, maxInput):
        for j in range(0, rowRange):
            ws.insert_rows(rowInsert)
        insertAndCopyRows(ws, rowInsert - rowRange, 1, ws.max_column + 1, rowRange)



#giống cái trên nhgwng thêm note
# Subnet #
# col cho ghi
# 2
def insertAndCopyRowRangeWithText(ws, maxInput, rowRange, rowInsert, text, col, startIndex):
    insertAndCopyRowRange(ws, maxInput, rowRange, rowInsert)
    for i in range(maxInput - 1):
        ws.cell(row=rowInsert + i * rowRange, column=col).value = text + str(startIndex)
        startIndex = startIndex + 1

#k dung
def insertAndCopyRowRangeV2(ws, maxInput, rowRange, rowInsert):
    ws.insert_rows(rowInsert, (maxInput-1)*rowRange)
    for i in range(1, maxInput):
        insertAndCopyRows(ws, rowInsert - rowRange, 1, ws.max_column + 1, rowRange)
        rowInsert += rowRange


#giống cáu insertAndCopyRowRangeWithText
def insertAndCopyRowRangeWithNo(ws, maxInput, rowRange, rowInsert):
    for i in range(1, maxInput):
        for j in range(0, rowRange):
            ws.insert_rows(rowInsert)
        insertAndCopyRowsWithNo(ws, rowInsert - rowRange, 1, ws.max_column + 1, rowRange, maxInput - i + 1)


# insert data
#value: list data
# rowStart: hàng bắt đầu
# col: cột bắt đầu
def fillData(ws, rowStart, col, value):
    j = 0
    for attr in value:
        ws.cell(row=rowStart + j, column=col).value = str(attr)
        j = j + 1