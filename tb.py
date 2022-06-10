# write append read  作用是什麼啊？
#20220403 新增 >> , << 
#20220404 新增 字串相加
#20220405 新增 for loop 格式{ for 已知變數/未知變數 = val/數值(運算) to 數值(運算) step 數值 }
#EX for x = 0 to 5 step 1 
#    ......( 可以有exitfor )
#   next
#20220423 新增gosub return (可以巢狀) 
#Ex gosub 行號
#    ....
#   return 
#20220515 新增while loop 格式{while 判斷式} (不能是bool) 且要有 Wend(可以巢狀)
#EX while a > 1
#   ......
#   Wend
#20220515 新增 SIN() COS() ABS() 是 rad
#20220517 新增 BOOL X?
#20220519 新增 STOP
#20220519 新增 FLOAT X@
#20220609 新增MAX,MIN

from operator import truediv
from math import cos, sin
from tracemalloc import start

VERSION = 1
#第一行的command 有hander處理
#rem 是註解行
reserved = ["LET", "PRINT", "INPUT", "IF", "GOTO","FOR","NEXT","EXITFOR","GOSUB","RETURN",
            "WHILE","WEND",
            "SLEEP", "END", "LIST", "REM", "READ",
            "WRITE", "APPEND", "RUN", "CLS", "CLEAR",
            "EXIT", "SAVE", "LOAD", "STOP"]
#op 有優先順序 分開左右,在判斷式中.越下面順位越高 類似語法樹
operators = [["==", "!=", ">", "<", ">=", "<="],
             ["."],
             ["+", "-" ,">>","<<"],
             ["*", "/", "&", "|", "%"],
             ["^"]]
MathFunction = ["SIN", "COS", "ABS","MAX","MIN"]
lines = {}  #暫存命令列 行號是key index 是 [命令,type]
array = {}  #儲存array  key是名稱 index 是[]
maxLine = 0
linePointer = 0
stopExecution = False
identifiers = {}
printReady = True
forLines = []
step = []
forValL = []
forValR = []
gosubLines = []
whileLine = {}


def main():
    print(f"Tiny BASIC version {VERSION}\nby Chung-Yuan Huang")
    while True:
            try:
                if printReady:
                    print("OK.")
                nextLine = input()
                if len(nextLine) > 0:
                    executeTokens(lex(nextLine)) 
            except KeyboardInterrupt:
                pass
            except SystemExit:
                print("Bye!")
                break
            except:
                print("Execution halted.")

def is_int(s):
    return int(s) == float(s)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_bool(s):
    if s.lower() == "true" :
        return True
    elif s.lower() == "false" :
        return True   
    else:
        return False

def getVarType(token):
    # 回傳 變數 賦值是什麼type 字串宣告為 x$ 正常數字變數為 x  浮點數為 x@  布林值為x?
    if len(token) > 1:
        if token[-1] == "$":
            return "STRING"
        elif token[-1] == "@":
            return "FLOAT"
        elif token[-1] == "?":
            return "BOOL"      
    return "NUM"

def isValidIdentifier(token): 
    #判斷是否符合命名規則 第一個英文後面英文或數字 ##字串變數結尾宣告為$
    if len(token) == 0:
        return False
    if len(token) > 1:
        if token[-1] == "$":
            token = token[0:-1]
        elif token[-1] == "@":
            token = token[0:-1]
        elif token[-1] == "?":
            token = token[0:-1]
    if not(token[0].lower() in "abcdefghijklmnopqrstuvwxyz"):
        return False
    for c in token[1:]:
        if not(token[0].lower() in "abcdefghijklmnopqrstuvwxyz0123456789"):
            return False
    return True
    
def lex(line):
    """
    分割command 一個一個讀入 並且 def 他的型態 
    ex: let x = 10
    let RESVD
    x   ID
    =   ASGN
    10  NUM
    tokens = [[let,TBD]]
    """
    inString = False
    tokens = []
    currentToken = ""
    line = line + " "
    for c in line:
        if not(inString) and c in " ()\"":
            if len(currentToken) != 0:
                tokens.append([currentToken, "TBD"])
                currentToken = ""
            if c == '"':
                inString = True
        elif inString and c == '"':
            tokens.append([currentToken, "STRING"])
            currentToken = ""
            inString = False
        else:
            currentToken += c
    # Le asigno un tipo a cada token
    for token in tokens:
        if token[1] != "TBD":
            continue
        value = token[0]
        if is_number(value):
            token[0] = float(token[0])
            token[1] = "NUM" #Number
        elif is_bool(value):
            if value.lower() == "true":
                token[0] = True
            else:
                token[0] = False
            token[1] = "BOOL" #Boolean
        elif value.upper() in reserved:
            #確認是不是在reserved中，有的話轉大寫
            token[0] = value.upper()
            token[1] = "RESVD" #Reserved word
        elif value.upper() in MathFunction:
            token[0] = value.upper()
            token[1] = "MF" #Math Function
        elif value.upper() == "THEN":
            token[0] = value.upper()
            token[1] = "THEN"
        elif value.upper() == "TO":
            token[0] = value.upper()
            token[1] = "TO"
        elif value.upper() == "STEP":
            token[0] = value.upper()
            token[1] = "STEP"
        elif value == "=":
            token[1] = "ASGN"
        elif isValidIdentifier(token[0]):#命名規則
            token[1] = "ID" #Identifier
        else:
            for i in range(0, len(operators)):
                if token[0] in operators[i]:
                    token[1] = "OP"
    return tokens

def executeTokens(tokens):
    #執行 輸入指令 且在reversed中 
    global lines, maxLine, stopExecution, linePointer, printReady
    printReady = True
    lineNumber = 0
    if tokens[0][1] == "NUM":
        lineNumber = int(tokens.pop(0)[0])
        if len(tokens) != 0:
            lines[lineNumber] = tokens
            if lineNumber > maxLine:
                maxLine = lineNumber
        else:
            lines.pop(lineNumber, None)
        printReady = False
        return
    if tokens[0][1] != "RESVD":
        print(f"Error: Unknown command {tokens[0][0]}.")
    else:
        command = tokens[0][0]
        if command == "REM":
            return
        elif command == "CLS":
            print("\n"*500)
        elif command == "END":
            stopExecution = True
        elif command == "EXIT":
            quit()
        elif command == "STOP":
            next = input()
            while True:
                if next.upper() == "RUN":
                    return 
                elif next.upper() == "QUIT":
                    quit()
                else:
                    next = input()
        elif command == "CLEAR":
            maxLine = 0
            lines = {}
            identifiers = {}
        elif command == "SAVE":
            if not(saveHandler(tokens[1:])): stopExecution = True
        elif command == "LOAD":
            if not(loadHandler(tokens[1:])): stopExecution = True
        elif command == "LIST":
            i = 0
            while i <= maxLine:
                if i in lines:
                    line = str(i)
                    for token in lines[i]:
                        tokenVal = "",
                        if token[1] == "NUM":
                            tokenVal = getNumberPrintFormat(token[0])
                        elif token[1] == "STRING":
                            tokenVal = f"\"{token[0]}\""
                        elif token[1] == "FLOAT":
                            tokenVal = getNumberPrintFormat(token[0])
                        elif token[1] == "BOOL":
                            tokenVal = f"\"{token[0]}\""
                        else:
                            tokenVal = token[0]
                        line += " " + str(tokenVal)
                    print(line)
                i = i + 1
        elif command == "PRINT":
            if not(printHandler(tokens[1:])): stopExecution = True
        elif command == "LET":
            if not(letHandler(tokens[1:])): stopExecution = True
        elif command == "INPUT":
            if not(inputHandler(tokens[1:])): stopExecution = True
        elif command == "GOTO":
            if not(gotoHandler(tokens[1:])): stopExecution = True
        elif command == "IF":
            if not(ifHandler(tokens[1:])): stopExecution = True
        elif command == "RUN":
            linePointer = 0
            while linePointer <= maxLine:
                if linePointer in lines:
                    executeTokens(lines[linePointer])
                    if stopExecution:
                        stopExecution = False
                        return
                linePointer = linePointer + 1
        elif command == "FOR":
            if not(forHandler(tokens[1:])): 
                stopExecution = True
            forLines.append(linePointer)
        elif  command == "NEXT":
            if not(nextHandler(tokens[1:])): stopExecution = True
        elif command == "EXITFOR":
            if not(exitforHandler()): stopExecution = True
        elif command == "GOSUB":
            if not(gosubHander(tokens[1:])): stopExecution = True
        elif command == "RETURN":
            if not(returnHander()): stopExecution = True
        elif command == "WHILE":
            if not(whileHandler(tokens[1:])): 
                stopExecution = True
        elif command == "WEND":
            if not(wendHandler()):stopExecution = True
#-----------------------------------------存檔----------------------------------
def saveHandler(tokens):
    i = 0
    filename = tokens[0][0]
    f = open(filename, 'w')
    while i <= maxLine:
        if i in lines:
            line = str(i)
            for token in lines[i]:
                tokenVal = "",
                if token[1] == "NUM":
                    tokenVal = getNumberPrintFormat(token[0])
                elif token[1] == "STRING":
                    tokenVal = f"\"{token[0]}\""
                else:
                    tokenVal = token[0]
                line += " " + str(tokenVal)
            f.write(line)
            f.write('\n')
        i = i + 1
    f.close()
    return True
#-----------------------------------------讀檔-----------------------------
def loadHandler(tokens):
    #print(tokens[0][0])
    global maxLine, lines, identifiers
    maxLine = 0
    lines = {}
    identifiers = {}
    filename = tokens[0][0]
    f = open(filename, 'r')
    for line in f.readlines():
        if len(line) > 0:
            executeTokens(lex(line))
    f.close()
    return True
#-------------------------------------------------------------------------------
def getNumberPrintFormat(num):
    # 如果是整數轉int 其他保持小數不變
    if int(num) == float(num):
        return int(num)
    return num
#---------------------- while 迴圈 ----------------------------------
def whileHandler(tokens):
    global whileLine,linePointer,lines,maxLine
    val_bool = solveExpression(tokens,0)# 回傳[bool,'NUM']
    tmpline = linePointer + 1
    count = 0
    while linePointer not in whileLine:
        if tmpline in lines:
            if lines[tmpline][0][0] == 'WHILE':
                count = count + 1
            if lines[tmpline][0][0] == 'WEND':
                if count == 0:
                    whileLine[linePointer] = tmpline
                    break
                else:
                    count = count - 1
            if  tmpline > maxLine :
                print ("Error:Expected WEND statement.")
                return False
        tmpline = tmpline + 1
    if(not val_bool[0]):
       linePointer = whileLine[linePointer]
    return True
def wendHandler():
    global linePointer,whileLine
    if whileLine :
        for key in whileLine.keys():
            if whileLine[key] == linePointer:
                linePointer = key - 1
                return True
        return False

    else :
        print("Error:Expected WHILE before statement.")
        return False
#----------------------這裡是 gosub and return 部分 :) ---------------------------
def returnHander():
    global gosubLines,linePointer
    if gosubLines :
        #print(gosubLines)
        linePointer = int(gosubLines.pop())
    else:
        linePointer = linePointer
    return True
def gosubHander(tokens):
    global linePointer,gosubLines,lines
    if tokens[0][0] in lines:
        gosubLines.append(linePointer)
        linePointer = int(tokens[0][0]-1)
        return True
    else :
        print ("Error: value of GOSUB statement is not find.")
        return False
#................從這裡開使都是for用到的function，不是老師原本的，可以不用看><.......................    
def exitforHandler():
    global linePointer,lines,forLines,forValL,forValR,step
    while linePointer < maxLine:
        linePointer = linePointer + 1
        if (lines[linePointer][0][0] == "NEXT"):
            clearfor()
            return linePointer
    print("Error: Malformed FOR statement.")
    return 
def nextHandler(tokens):
    global forValL,forValR,linePointer
    if forValL[len(forValL)-1][1] == "NUM":
        tmpValL = forValL[len(forValL)-1][0]
    elif forValL[len(forValL)-1][1] == "ID":
        tmpValL = getIdentifierValue(forValL[len(forValL)-1][0])[0]
    tmpValR = forValR[len(forValR)-1]
    # 前面有 FOR
    if(len(step) != 0 and len(forLines) != 0):
        if(tmpValL+step[len(step)-1] < tmpValR):
            if forValL[len(forValL)-1][1] == "NUM":
                forValL[len(forValL)-1][0] = forValL[len(forValL)-1][0] + step[len(step)-1] 
            elif forValL[len(forValL)-1][1] == "ID":
                identifiers[forValL[len(forValL)-1][0]][0] = getIdentifierValue(forValL[len(forValL)-1][0])[0] + step[len(step)-1]
            linePointer  = forLines[len(forLines)-1]
        else :
            clearfor()
        return True
    # 前面沒有FOR
    else :
        print("Error: Expected expression.")
        return
def clearfor():
    global forLines,forValL,forValR,step
    forValR.pop(),forValL.pop(),forLines.pop(),step.pop()
    return
def forHandler(tokens):
    global step,forValL,forValR
    tmpValL = None
    tmpValR = None
    toPos = None
    stepPos = None
    asgnPos = None
    for i in range(0,len(tokens)):
        if(tokens[i][1] == "TO"):
            toPos = i
        if(tokens[i][1] == "STEP"):
            stepPos = i
        if(tokens[i][1] == "ASGN"):
            asgnPos = i
    if toPos == None:
        print("Error: Malformed FOR statement.")
        return
    if stepPos == None:
        print("Error: Malformed FOR statement.")
        return
    if asgnPos == None and tokens[toPos - 1][1] == "NUM":
        tmpValL = solveExpression(tokens[0:toPos], 0)
        #tmpValL = [tokens[toPos - 1][0],"NUM"]
    elif asgnPos == None and tokens[toPos - 1][1] == "ID":
        tmpValL = getIdentifierValue(tokens[toPos - 1][0])
    elif tokens[asgnPos - 1][1] == "ID" and tokens[asgnPos + 1][1] == "NUM":
        tmpR = solveExpression(tokens[asgnPos+1:toPos], 0)
        getIdentifierValue(tokens[asgnPos - 1][0])
        identifiers[tokens[asgnPos-1][0]][0] = tmpR[0]
        tmpValL = tokens[asgnPos-1]
    else:
        print("Error: Malformed FOR statement.")
        return
    if tokens[toPos + 1][1] == "NUM" :
        if stepPos == None:
            tmpValR= solveExpression(tokens[toPos+1:], 0)
        else :
            tmpValR = solveExpression(tokens[toPos+1:stepPos], 0)
        if tokens[stepPos + 1][1] == "NUM" :
            step.append(tokens[stepPos + 1][0])
        else :
            print("Error: Malformed FOR statement.")
            return
    else :
        print("Error: Malformed FOR statement.")
        return
    forValL.append(tmpValL)
    forValR.append(tmpValR[0])
    return True
#..............結束.......................................
def gotoHandler(tokens):
    global linePointer
    if len(tokens) == 0:
        print("Error: Expected expression.")
        return
    newNumber = solveExpression(tokens, 0)
    if newNumber[1] != "NUM":
        print("Error: Line number expected.")
    else:
        linePointer = newNumber[0] - 1
    return True

def inputHandler(tokens):
    #修改identifier 的 value
    varName = None
    if len(tokens) == 0:
        print("Error: Expected identifier.")
        return
    elif len(tokens) == 1 and tokens[0][1] == "ID":
        varName = tokens[0][0]
    else:
        varName = solveExpression(tokens, 0)[0]
        if not(isValidIdentifier(varName)):
            print(f"Error: {varName} is not a valid identifier.")
            return
    while True:
        print("?")
        #print("?", end = '') #原本預設為反斜線n換行
        varValue = input()
        if getVarType(varName) == "STRING":
            identifiers[varName] = [varValue, "STRING"]
            break
        elif getVarType(varName) == "FLOAT":
            identifiers[varName] = [varValue, "FLOAT"]
            break
        elif getVarType(varName) == "BOOL":
            identifiers[varName] = [varValue, "BOOL"]
            break
        else:
            if is_number(varValue):
                identifiers[varName] = [varValue, "NUM"]
                break
            else:
                print("Try again.")
    return True

def ifHandler(tokens):
    # if .. then ..
    thenPos = None
    for i in range(0, len(tokens)):
        if tokens[i][1] == "THEN":
            thenPos = i
            break
    if thenPos == None:
        print("Error: Malformed IF statement.")
        return
    exprValue = solveExpression(tokens[0:thenPos], 0)
    #print(exprValue)
    if exprValue == None:
        return
    elif exprValue[0] != 0:
        if len(tokens[i+1:]) == 0:
            print("Error: Malformed IF statement.")
            return      
        executeTokens(tokens[i+1:])
    return True

def letHandler(tokens):
    # 把變數名稱跟變數值放入 identifiers
    varName = None
    varValue = None
    eqPos = None
    for i in range(0, len(tokens)):
        if tokens[i][1] ==  "ASGN":
            eqPos = i
            break
    if eqPos == None:
        print("Error: Malformed LET statement.")
        return
    if eqPos == 1 and tokens[0][1] == "ID":
        varName = tokens[0][0]
    else:
        if len(tokens[0:i]) == 0:
            print("Error: Expected identifier.")
            return
        varName = solveExpression(tokens[0:i], 0)
        if varName == None:
            stopExecution = True
            return
        varName = varName[0]
        if not(isValidIdentifier(varName)):
            print(f"Error: {varName} is not a valid identifier.")
            return
    if len(tokens[i+1:]) == 0:
        print("Error: Expected expression.")
        return
    varValue = solveExpression(tokens[i+1:], 0)
    if varValue == None:
        return
    if getVarType(varName) != varValue[1]:
        if(getVarType(varName)=="FLOAT" and varValue[1]=="NUM"):
            identifiers[varName] = varValue
            return True
        else:
            print(f"Error: Variable {varName} type mismatch.")
            return
    identifiers[varName] = varValue
    return True

def printHandler(tokens):
    # print 輸出,
    if len(tokens) == 0:
        print("Error: Expected identifier.")
        return
    exprRes = solveExpression(tokens, 0)
    if exprRes == None:
        return
    if exprRes[1] == "NUM":
        exprRes[0] = getNumberPrintFormat(exprRes[0])
    print(exprRes[0])
    return True

def getIdentifierValue(name):
    global identifiers
    # 取變數值 return [value,"NUM"]
    try:
        return identifiers[name]
    except KeyError:
        identifiers[name] = [0, "NUM"]
        return  identifiers[name]
         

def solveExpression(tokens, level):
    #把變數的東西運算完 再回傳值和type [10,'NUM']
    leftSideValues = []
    rightSideValues = []
    if level < len(operators):
        for i in range(0, len(tokens)):
            if not(tokens[i][1] in ["OP", "NUM", "STRING", "ID", "FLOAT", "BOOL", "MF"]):
                print(f"Error: Unknown operand {tokens[i][0]}")
                return None
            elif tokens[i][1] == "MF" and tokens[i][0] in MathFunction[level]:
                if tokens[i+1][1] != "NUM" and tokens[i+1][1] != "ID":
                    print("Error: NUM expects value in " +tokens[i][0]+ " ().")
                    return None
                if tokens[i][0] == "ABS":
                    if tokens[i+1][1] == "NUM":
                        leftSideValues.append([abs(tokens[i+1][0]), "NUM"])
                    elif tokens[i+1][1] == "ID":
                        print(getIdentifierValue(tokens[i+1][0]))
                        leftSideValues.append([abs(getIdentifierValue(tokens[i+1][0])[0]), "NUM"])
                    i=i+1
                elif tokens[i][0] == "SIN":
                    if tokens[i+1][1] == "NUM":
                        leftSideValues.append([sin(tokens[i+1][0]), "NUM"])
                    elif tokens[i+1][1] == "ID":
                        print(getIdentifierValue(tokens[i+1][0]))
                        leftSideValues.append([sin(getIdentifierValue(tokens[i+1][0])[0]), "NUM"])
                    i=i+1
                elif tokens[i][0] == "COS":
                    if tokens[i+1][1] == "NUM":
                        leftSideValues.append([cos(tokens[i+1][0]), "NUM"])
                    elif tokens[i+1][1] == "ID":
                        print(getIdentifierValue(tokens[i+1][0]))
                        leftSideValues.append([cos(getIdentifierValue(tokens[i+1][0])[0]), "NUM"])
                    i=i+1
                elif tokens[i][0] == "MAX":
                    tmp = 0 
                    start = 0
                    loc = i
                    while start < len(tokens) - i - 1 : 
                            if tokens[loc+1][1] == "NUM" :
                                val = tokens[loc+1] 
                            elif tokens[loc+1][1] == "ID" :
                                val = getIdentifierValue(tokens[loc+1][0])
                            tmp = max(tmp,val[0])
                            start += 1
                            loc += 1
                    leftSideValues.append([tmp, "NUM"])
                    i=i+1
                elif tokens[i][0] == "MIN":
                    tmp = 0 
                    start = 0
                    loc = i
                    while start < len(tokens) - i - 1 : 
                            if tokens[loc+1][1] == "NUM" :
                                val = tokens[loc+1] 
                            elif tokens[loc+1][1] == "ID" :
                                val = getIdentifierValue(tokens[loc+1][0])
                            tmp = min(tmp,val[0])
                            start += 1
                            loc += 1
                    leftSideValues.append([tmp, "NUM"])
                    i=i+1
            elif tokens[i][1] == "OP" and tokens[i][0] in operators[level]:
                exprResL = None
                exprResR = None
                #用operator分左右 不斷遞迴  
                if len(leftSideValues) != 0:
                    exprResL = solveExpression(leftSideValues, level)
                rightSideValues = tokens[i+1:]
                if len(rightSideValues) != 0:
                    exprResR = solveExpression(rightSideValues, level)
                if exprResL == None or exprResR == None:
                    return None
                if tokens[i][0] == ">>":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM" and is_int(exprResL[0]):
                        return [int(exprResL[0] / 2**exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "<<":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM" and is_int(exprResL[0]):
                        return [int(exprResL[0] * 2**exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None       
                elif tokens[i][0] == "+":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) + float(exprResR[0]), "NUM"]
                    elif exprResL[1] == "STRING" and exprResR[1] == "STRING":
                        return [exprResL[0]+exprResR[0] ,"STRING"]
                    else:    
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "-":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) - float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "/":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) / float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None 
                elif tokens[i][0] == "*":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) * float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None     
                elif tokens[i][0] == "^":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) ** float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "%":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) % float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "==":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] == exprResR[0], "NUM"]
                elif tokens[i][0] == "!=":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] != exprResR[0], "NUM"]
                elif tokens[i][0] == "<=":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] <= exprResR[0], "NUM"]
                elif tokens[i][0] == "<":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] < exprResR[0], "NUM"]
                elif tokens[i][0] == ">":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] > exprResR[0], "NUM"]
                elif tokens[i][0] == ">=":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] >= exprResR[0], "NUM"]
                elif tokens[i][0] == "&":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [(exprResL[0]) and (exprResR[0]), "NUM"]
                    elif exprResL[1] == "BOOL" and exprResR[1] == "BOOL":
                        return [(exprResL[0]) and (exprResR[0]), "BOOL"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "|":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [(exprResL[0]) or (exprResR[0]), "NUM"]
                    elif exprResL[1] == "BOOL" and exprResR[1] == "BOOL":
                        return [(exprResL[0]) or (exprResR[0]), "BOOL"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == ".":
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        value1 = exprResL[0]
                        if exprResL[1] == "NUM":
                            value1 = str(getNumberPrintFormat(value1))
                        value2 = exprResR[0]
                        if exprResR[1] == "NUM":
                            value2 = str(getNumberPrintFormat(value2))
                        return [value1 + value2, "STRING"]
                
            else:
                leftSideValues.append(tokens[i])
        return solveExpression(leftSideValues, level + 1)
    else:
        if tokens[0][1] == "ID":
            if tokens[0][0] in identifiers:
                return getIdentifierValue(tokens[0][0])
            else:
                print(f"Error: Variable {tokens[0][0]} not initialized.")
                return None
        return tokens[0]

main()
