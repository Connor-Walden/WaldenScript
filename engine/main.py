from wdscript import WaldenScript

import sys

defaultFuncs = [ 'print' ]
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

        if(item[0] == 'call function'):
            call_func(variables, functions, item)

    if(entryMethod != None):
        call_func(variables, functions, entryMethod)

def call_func(variables, functions, item):
    if(item[1] in defaultFuncs):
        if(item[1] == 'print'):
            if('"' not in item[2][0] and "'" not in item[2][0]):
                varFound = False

                for var in variables:
                    if(var[1] == item[2][0]):
                        varFound = True

                        if(var[0] == 'string'):
                            print(WALDENSCRIPT_OUT_PREFIX + var[2][1:-1])
                        else:
                            print(WALDENSCRIPT_OUT_PREFIX + str(var[2]))
                
                if(varFound == False): # no print operation has taken place, ie numbers
                    print(WALDENSCRIPT_OUT_PREFIX + str(item[2][0]))
            else:
                print(WALDENSCRIPT_OUT_PREFIX + item[2][0][1:-1])
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

                        variables.append([varType, varName, varValue])
                    elif(bodyItem[0] == 'assign result of binary operation'):                        
                        varNameToUpdate = bodyItem[1]
                        leftOperand = bodyItem[2]

                        rightOperand = bodyItem[4]
                        operation = bodyItem[3]

                        for var in variables:
                            if(var[1] == varNameToUpdate):
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

                    elif(bodyItem[0] == 'assignment'):                           
                        varNameToUpdate = bodyItem[1]
                        value = bodyItem[2]

                        for var in variables:
                            if(var[1] == varNameToUpdate):
                                var[2] = value
                                break 

                    elif(bodyItem[0] == 'call function'):
                        call_func(variables, functions, bodyItem)
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