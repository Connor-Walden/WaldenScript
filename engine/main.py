from wdscript import WaldenScript

import sys

defaultFuncs = [ 'out', 'in' ]
WALDENSCRIPT_OUT_PREFIX = 'OUT > '
ERROR_PREFIX = 'ERR > '

def main():
    script = WaldenScript()
    ast = script.read(sys.argv[1])

    variables = []
    functions = []
    
    entryMethod = None

    for item in ast:
        if(item[0] == 'init function'):
            funcType = item[1]
            funcName = item[2]
            funcArgs = item[3]
            funcBody = item[4]

            functions.append([funcType, funcName, funcArgs, funcBody])

            if(funcName == 'entry'):
                entryMethod = [ 'call function', funcName, [] ]

    if(entryMethod != None):
        call_func(variables, functions, entryMethod, 'entry', []) # entry - only way to begin a WD program
    else:
        print(ERROR_PREFIX + 'NO ENTRY >:( | please add a [void entry() -> {}] to your program to begin!')
   
def call_func(variables, functions, item, scope, params):
    if(item[1] in defaultFuncs):
        if(item[1] == 'out'):
            if('"' not in item[2][0] and "'" not in item[2][0]):
                varFound = False

                for var in variables:
                    if(var[1] == item[2][0]):
                        for func in functions:
                            if(func[1] == var[3]):  
                                if(var[3] == item[3] or var[1] in params):
                                    varFound = True

                                    if(var[0] == 'string'):
                                        print(WALDENSCRIPT_OUT_PREFIX + var[2][1:-1])
                                    else:
                                        print(WALDENSCRIPT_OUT_PREFIX + str(var[2]))      
                                else:
                                    print(ERROR_PREFIX + 'variable "' + item[2][0] + '" does not exist in this scope :(')
                                    return False

                if(varFound == False): # no print operation has taken place, ie numbers
                    if('"' in item[2][0] or "'" in item[2][0]):                
                        print(WALDENSCRIPT_OUT_PREFIX + item[2][0][1:-1])
                    else:
                        print(WALDENSCRIPT_OUT_PREFIX + str(item[2][0]))
            else:
                for func in functions:
                    if(func[1] == scope):
                        if(var[3] == scope or var[1] in params):
                            if('"' in item[2][0] or "'" in item[2][0]):                
                                print(WALDENSCRIPT_OUT_PREFIX + item[2][0][1:-1])
                            else:                
                                print(WALDENSCRIPT_OUT_PREFIX + str(item[2][0]))
                                
    else:
        funcName = item[1]

        funcFound = False

        for func in functions:
            if(func[1] == funcName):
                funcFound = True

                funcParams = func[2]
                funcBody = func[3]

                for bodyItem in funcBody:
                    if(bodyItem[0] == 'init variable'):
                        varType = bodyItem[1]
                        varName = bodyItem[2]
                        varValue = bodyItem[3]
                        varConst = bodyItem[4]

                        variables.append([varType, varName, varValue, funcName, varConst])
                    elif(bodyItem[0] == 'init variable to result of binary operation'):
                        varType = bodyItem[1]
                        varName = bodyItem[2]
                        varValue = bodyItem[3]
                        varOp = bodyItem[4]
                        varValue2 = bodyItem[5]
                        varConst = bodyItem[6]
                        
                        variable = [varType, varName, varValue, funcName, varConst]
                        variables.append(variable)
                        
                        bodyItemForBinOp = ['assign result of binary operation', varName, varValue, varOp, varValue2, False]
                        binary_operation(variables, functions, bodyItemForBinOp, funcName, params, False)
                    elif(bodyItem[0] == 'assign result of binary operation'):       
                        binary_operation(variables, functions, bodyItem, funcName, params, True)

                    elif(bodyItem[0] == 'assignment'):                           
                        varNameToUpdate = bodyItem[1]
                        value = bodyItem[2]

                        for var in variables:
                            if(var[1] == varNameToUpdate): 
                                if(var[3] == funcName or varNameToUpdate in params):
                                    if(var[4] == False):
                                        var[2] = value
                                    else:
                                        print(ERROR_PREFIX + 'cannot edit a constant variable: ' + varNameToUpdate)
                                        return False
                                    break 
                                else:
                                    print(ERROR_PREFIX + 'variable "' + varNameToUpdate + '" does not exist in this scope :(')
                                    return False

                    elif(bodyItem[0] == 'call function'):
                        if(bodyItem[1] in defaultFuncs):

                            notNumber = True

                            for char in bodyItem[2][0]:
                                if(char in '1234567890.'):
                                    notNumber = False

                            if('"' not in bodyItem[2][0] and "'" not in bodyItem[2][0] and notNumber):
                                paramFound = False

                                if len(params) == 0:
                                    if(funcName == bodyItem[3]):
                                        paramFound = True

                                        if(call_func(variables, functions, bodyItem, scope, []) == False):
                                            return
                                else:      
                                    for param in bodyItem[2]:
                                        if(param in params):
                                            paramFound = True
                                            
                                            if(call_func(variables, functions, bodyItem, scope, bodyItem[2]) == False):
                                                return

                                if(paramFound == False):
                                    print(ERROR_PREFIX + 'variable "' + bodyItem[2][0] + '" does not exist in this scope :(')
                                    return False
                            else:
                                if(call_func(variables, functions, bodyItem, scope, bodyItem[2]) == False):
                                    return

                        else: # default func get scope of parent method
                            if(len(bodyItem[2]) == 0):
                                if(call_func(variables, functions, bodyItem, funcName, []) == False):
                                    return
                            else:
                                # get function and only accept the right params
                                foundFunc = False

                                for func in functions:
                                    if func[1] == bodyItem[1]:
                                        # filter params
                                        foundFunc = True
                                        paramList = []

                                        for param in func[2]:
                                            for param2 in bodyItem[2]:
                                                if(param == param2):
                                                    paramList.append(param)

                                        allValid = False
                                        for param in paramList:
                                            for var in variables:
                                                if var[1] == param:
                                                    if(var[3] == funcName or var[1] in params):
                                                        allValid = True
                                        idx = 0
                                        while idx < len(bodyItem[2]):
                                            if(bodyItem[2][idx+1] == 'colon'):
                                                map_var(variables, bodyItem[2][idx], bodyItem[2][idx+2], funcName)
                                                idx += 3
                                                allValid = True
                                            else:
                                                idx += 1
                                                
                                        if allValid:    
                                            if(call_func(variables, functions, bodyItem, funcName, paramList) == False):
                                                return
                                        else:
                                            print(ERROR_PREFIX + 'variable "' + bodyItem[2][0] + '" does not exist in this scope :(')
                                            return False
                                if(foundFunc == False):
                                    print(ERROR_PREFIX + 'Method does not exist! ("' + bodyItem[1] + '")')
                break  

        if(funcFound == False):
            print(ERROR_PREFIX + 'Method does not exist! ("' + funcName + '")')

def map_var(variables, left, right, scope):
    mapped = False
    for var in variables:
        if var[1] == right:
            variables.append([var[0], left, var[2], var[3], var[4]])    
            mapped = True
            
    if(mapped == False):
        if('"' in right or "'" in right):
            variables.append(['string', left, right, scope, True])
        else:
            isNumber = True
            for char in right:
                if char not in '0123456789.':
                    isNumber = False
                    
            if(isNumber):
                variables.append(['number', left, right, scope, True])
            
def binary_operation(variables, functions, bodyItem, funcName, params, enforceConstant):
    varNameToUpdate = bodyItem[1]
    leftOperand = bodyItem[2]
    rightOperand = bodyItem[4]

    for var in variables:
        if(var[1] == leftOperand):
            leftOperand = var[2]
        
        if(var[1] == rightOperand):
            rightOperand = var[2]

    operation = bodyItem[3]

    for var in variables:
        if(var[1] == varNameToUpdate):
            for func in functions:
                if(func[1] == funcName):
                    if(var[3] == funcName or varNameToUpdate in params):
                        if(var[4] == False or enforceConstant == False):
                            left = get_left(leftOperand, variables)
                            right = get_right(rightOperand, variables)

                            isStr = False
                            if('"' in str(left)[-1] or "'" in str(left)[-1]):
                                isStr = True
                                left = left[:-1]

                            if('"' in str(right)[0] or "'" in str(right)[0]):
                                isStr = True
                                right = right[1:]

                            if(isStr):
                                if(operation == 'plus'):
                                    var[2] = left + right
                                    break
                                if(operation == 'minus'):
                                    print(ERROR_PREFIX + 'cannot perform a "-" operation on strings')
                                    return False
                                if(operation == 'multiply'):
                                    print(ERROR_PREFIX + 'cannot perform a "*" operation on strings')
                                    return False
                                if(operation == 'divide'):
                                    print(ERROR_PREFIX + 'cannot perform a "/" operation on strings')
                                    return False
                            else:
                                
                                numLeft = None
                                if '.' in var[2]:
                                    numLeft = float(left)    
                                else:
                                    numLeft = int(left)   
                                    
                                numRight = None
                                if '.' in var[2]:
                                    numRight = float(right)    
                                else:
                                    numRight = int(right)                                 
                                
                                if(operation == 'plus'):
                                    var[2] = numLeft + numRight
                                    break
                                if(operation == 'minus'):
                                    var[2] = numLeft - numRight
                                    break
                                if(operation == 'multiply'):
                                    var[2] = numLeft * numRight
                                    break
                                if(operation == 'divide'):
                                    var[2] = numLeft / numRight
                                    break
                        else:
                            print(ERROR_PREFIX + 'cannot edit a constant variable: ' + varNameToUpdate)
                            return False
                        
                    else:
                        print(ERROR_PREFIX + 'variable "' + varNameToUpdate + '" does not exist in this scope :(')
                        return False

def get_left(leftOperand, variables):
    left = leftOperand

    for var in variables:
        if(var[1] == leftOperand):
            if('"' in var[2] or "'" in var[2]):
                left = str(var[2])
            elif('.' in var[2]):
                left = float(var[2])
            else:
                left = int(var[2])

    return left

def get_right(rightOperand, variables):
    right = rightOperand

    for var in variables:
        if(var[1] == rightOperand):
            if('"' in var[2] or "'" in var[2]):
                right = str(var[2])
            elif('.' in var[2]):
                right = float(var[2])
            else:
                right = int(var[2])
                
    return right

main()