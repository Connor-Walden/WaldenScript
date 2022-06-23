from wdscript import WaldenScript

import sys

defaultFuncs = [ 'out' ]
WALDENSCRIPT_OUT_PREFIX = 'WD > '

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
        call_func(variables, functions, entryMethod, 'entry', [])

def call_func(variables, functions, item, scope, params):
    if(item[1] in defaultFuncs):
        if(item[1] == 'out'):
            if('"' not in item[2][1:-1] and "'" not in item[2][0]):
                varFound = False

                for var in variables:
                    if(var[1] == item[2][0]):
                        for func in functions:
                            if(func[1] == scope):
                                if(var[3] == scope or var[1] in params):
                                    varFound = True

                                    if(var[0] == 'string'):
                                        print(WALDENSCRIPT_OUT_PREFIX + var[2][1:-1])
                                    else:
                                        print(WALDENSCRIPT_OUT_PREFIX + str(var[2]))      
                                else:
                                    print('RUNTIME ERROR - variable "' + item[2][0] + '" does not exist in this scope :(')
                                    return False

                if(varFound == False): # no print operation has taken place, ie numbers
                    if('"' in item[2][0] or "'" in item[2][0]):                
                        print(WALDENSCRIPT_OUT_PREFIX + item[2][0][1:-1])
                    else:
                        print(WALDENSCRIPT_OUT_PREFIX + str(item[2][0]))
            else:
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

                        variables.append([varType, varName, varValue, funcName])
                    elif(bodyItem[0] == 'assign result of binary operation'):                        
                        varNameToUpdate = bodyItem[1]
                        leftOperand = bodyItem[2]

                        rightOperand = bodyItem[4]
                        operation = bodyItem[3]

                        for var in variables:
                            if(var[1] == varNameToUpdate):
                                for func in functions:
                                    if(func[1] == funcName):
                                        if(var[3] == funcName or varNameToUpdate in params):
                                            left = get_left(leftOperand, variables)
                                            right = get_right(rightOperand, variables)

                                            if(operation == 'plus'):
                                                var[2] = left + right
                                                break
                                            if(operation == 'minus'):
                                                var[2] = left - right
                                                break
                                            if(operation == 'multiply'):
                                                var[2] = left * right
                                                break
                                            if(operation == 'divide'):
                                                var[2] = left / right
                                                break
                                        else:
                                            print('RUNTIME ERROR - variable "' + varNameToUpdate + '" does not exist in this scope :(')


                    elif(bodyItem[0] == 'assignment'):                           
                        varNameToUpdate = bodyItem[1]
                        value = bodyItem[2]

                        for var in variables:
                            if(var[1] == varNameToUpdate): 
                                if(var[3] == funcName):
                                    var[2] = value
                                    break 
                                else:
                                    print('RUNTIME ERROR - variable "' + varNameToUpdate + '" does not exist in this scope :(')

                    elif(bodyItem[0] == 'call function'):
                        if(bodyItem[1] in defaultFuncs):

                            notNumber = True

                            for char in bodyItem[2][0]:
                                if(char in '1234567890.'):
                                    notNumber = False

                            if('"' not in bodyItem[2][0] and "'" not in bodyItem[2][0] and notNumber):
                                paramFound = False

                                for param in bodyItem[2]:
                                    if(param in params):
                                        paramFound = True

                                        if(call_func(variables, functions, bodyItem, scope, bodyItem[2]) == False):
                                            return

                                if(paramFound == False):
                                    print('RUNTIME ERROR - variable "' + bodyItem[2][0] + '" does not exist in this scope :(')
                                    return
                            else:
                                if(call_func(variables, functions, bodyItem, scope, bodyItem[2]) == False):
                                    return

                        else: # default func get scope of parent method
                            if(len(bodyItem[2]) == 0):
                                if(call_func(variables, functions, bodyItem, funcName, []) == False):
                                    return
                            else:
                                # get function and only accept the right params

                                for func in functions:
                                    if func[1] == bodyItem[1]:
                                        # filter params

                                        paramList = []

                                        for param in func[2]:
                                            for param2 in bodyItem[2]:
                                                if(param == param2):
                                                    paramList.append(param)

                                        if(call_func(variables, functions, bodyItem, funcName, paramList) == False):
                                            return
                break  

        if(funcFound == False):
            print('RUNTIME ERROR: Method does not exist! ("' + funcName + '")')

def get_left(leftOperand, variables):
    left = leftOperand
    found = False
    for var in variables:
        if(var[1] == leftOperand):
            found = True

            if('.' in var[2]):
                left = float(var[2])
            else:
                left = int(var[2])
    
    if(found == False):
        if('.' in leftOperand):
            left = float(leftOperand)
        else:
            left = int(leftOperand)

    return left

def get_right(rightOperand, variables):
    right = rightOperand
    found = False
    if('.' in rightOperand):
        right = float(rightOperand)
    else:
        right = int(rightOperand)

    if(found == False):
        if('.' in rightOperand):
            right = float(rightOperand)
        else:
            right = int(rightOperand)

    for var in variables:
        if(var[1] == rightOperand):
            if('.' in var[2]):
                right = float(var[2])
            else:
                right = int(var[2])

    return right


main()