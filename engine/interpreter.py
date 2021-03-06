from six.moves import input

defaultFuncs = [ 'out', 'in', 'if' ]

WALDENSCRIPT_OUT_PREFIX = ''
WALDENSCRIPT_IN_PREFIX = ''
ERROR_PREFIX = 'ERR > '

class Interpreter:
    def __init__(self):
        self.variables = []
        self.functions = []
        self.mapped = []
        
    def interpret(self, ast):
        entryMethod = None

        for item in ast:
            if(item[0] == 'init function'):
                funcType = item[1]
                funcName = item[2]
                funcArgs = item[3]
                funcBody = item[4]

                self.functions.append([funcType, funcName, funcArgs, funcBody])

                if(funcName == 'entry'):
                    entryMethod = [ 'call function', funcName, [] ]

        if(entryMethod != None):
            self.call_func(entryMethod, 'entry', []) # entry - only way to begin a WD program
        else:
            print(ERROR_PREFIX + 'NO ENTRY >:( | please add a [void entry() -> {}] to your program to begin!')        
        
    def call_func(self, item, scope, params):
        if(item[1] in defaultFuncs):
            self.call_default_func(item, scope, params)
        else:
            funcName = item[1]

            funcFound = False

            for func in self.functions:
                if(func[1] == funcName):
                    funcFound = True
                    funcBody = func[3]

                    self.interpret_body(funcName, funcBody, scope, params)
                    break
            if(funcFound == False):
                print(ERROR_PREFIX + 'Method does not exist! ("' + funcName + '")')
            
    def call_default_func(self, item, scope, params):
        if(item[1] == 'out'):
            if('"' not in item[2][0] and "'" not in item[2][0]):
                varFound = False
                
                allVariables = self.variables + self.mapped

                for var in allVariables:
                    if(var[1] == item[2][0]):
                        for func in self.functions:
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
                for func in self.functions:
                    if(func[1] == scope):         
                        print(WALDENSCRIPT_OUT_PREFIX + str(item[2][0][1:-1]))
        elif(item[1] == 'if'):
            value1 = item[2][0]
            conditional = item[2][1]
            value2 = item[2][2]
            
            for var in self.variables:
                if(var[1] == item[2][0]):
                    value1 = var[2]
                elif(var[1] == item[2][2]):
                    value2 = var[2]
        
            if(conditional == 'equals'):   
                if(value1 == value2):
                    self.interpret_body(item[3], item[4], item[3], [])
                                
    def interpret_body(self, funcName, funcBody, scope, params):
        for bodyItem in funcBody:
            if(bodyItem[0] == 'init variable'):
                varType = bodyItem[1]
                varName = bodyItem[2]
                varValue = bodyItem[3]
                varConst = bodyItem[4]

                exists = False
                for var in self.variables:
                    if var[1] == varName:
                        exists = True
                    
                if(exists == False):        
                    self.variables.append([varType, varName, varValue, funcName, varConst])
                else:
                    print(ERROR_PREFIX + 'Variable already exists... ' + varName)
                    return False
            elif(bodyItem[0] == 'init variable to result of binary operation'):
                varType = bodyItem[1]
                varName = bodyItem[2]
                varValue = bodyItem[3]
                varOp = bodyItem[4]
                varValue2 = bodyItem[5]
                varConst = bodyItem[6]
                
                variable = [varType, varName, varValue, funcName, varConst]
                self.variables.append(variable)
                
                bodyItemForBinOp = ['assign result of binary operation', varName, varValue, varOp, varValue2, False]
                self.binary_operation(bodyItemForBinOp, funcName, params, False)
            elif(bodyItem[0] == 'assign result of binary operation'):       
                self.binary_operation(bodyItem, funcName, params, True)
            elif(bodyItem[0] == 'init variable to result of user input'):
                varType = bodyItem[1]
                varName = bodyItem[2]
                varText = bodyItem[3]
                varConst = bodyItem[4]
                
                uIn = '"' + input(WALDENSCRIPT_IN_PREFIX + varText + ': ') + '"'

                variable = [varType, varName, uIn, funcName, varConst]
                self.variables.append(variable)                     
            elif(bodyItem[0] == 'assignment'):                           
                varNameToUpdate = bodyItem[1]
                value = bodyItem[2]

                for var in self.variables:
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

                        for param in bodyItem[2]:
                            if(param in params):
                                paramFound = True
                                
                        if(paramFound):
                            if(self.call_func(bodyItem, scope, bodyItem[2]) == False):
                                return

                        if(paramFound == False):
                            if(bodyItem[1] == 'if'):
                                
                                inScope = False
                                
                                for var in self.variables:
                                    if var[1] == bodyItem[2][0]:
                                        if(funcName == var[3]):
                                            inScope = True
                                
                                for var in self.mapped:
                                    if var[1] == bodyItem[2][0]:
                                        if(funcName == var[3]):
                                            inScope = True
                                            
                                if funcName == scope:
                                    inScope = True
                                            
                                if(inScope):
                                    paramFound = True
                                    
                                    if(self.call_func(bodyItem, scope, []) == False):
                                        return
                                else:
                                    print(ERROR_PREFIX + 'variable "' + bodyItem[2][0] + '" does not exist in this scope :(')
                                    return False
                            else:
                                if(funcName == bodyItem[3]):
                                    paramFound = True
                                    
                                    if(self.call_func(bodyItem, scope, []) == False):
                                        return
                                else:             
                                    print(ERROR_PREFIX + 'variable "' + bodyItem[2][0] + '" does not exist in this scope :(')
                                    return False
                    else:
                        if(self.call_func(bodyItem, scope, bodyItem[2]) == False):
                            return

                else: # default func get scope of parent method
                    if(len(bodyItem[2]) == 0):
                        if(self.call_func(bodyItem, funcName, []) == False):
                            return
                    else: 
                        # get function and only accept the right params
                        foundFunc = False

                        for func in self.functions:
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
                                    for var in self.variables:
                                        if var[1] == param:
                                            if(var[3] == funcName or var[1] in params):
                                                allValid = True
                                idx = 0
                                while idx < len(bodyItem[2]) - 1:
                                    if(bodyItem[2][idx+1] == 'colon'):
                                        self.map_var(bodyItem[2][idx], bodyItem[2][idx+2], funcName)
                                        idx += 3
                                        allValid = True
                                    else:
                                        idx += 1
                                        
                                if allValid:    
                                    if(self.call_func(bodyItem, funcName, paramList) == False):
                                        return
                                else:
                                    print(ERROR_PREFIX + 'variable "' + bodyItem[2][0] + '" does not exist in this scope :(')
                                    return False
                        if(foundFunc == False):
                            print(ERROR_PREFIX + 'Method does not exist! ("' + bodyItem[1] + '")')

    def map_var(self, left, right, scope):
        isVar = False
        for var in self.variables:
            if var[1] == right:
                self.mapped.append([var[0], left, var[2], var[3], var[4]])    
                isVar = True
                
        if(isVar == False):
            if('"' in right or "'" in right):
                self.mapped.append(['string', left, right, scope, True])
            else:
                isNumber = False
                for char in right:
                    if char in '0123456789.':
                        isNumber = True
                        
                if(isNumber):
                    self.mapped.append(['number', left, right, scope, True])
                
    def binary_operation(self, bodyItem, funcName, params, enforceConstant):
        varNameToUpdate = bodyItem[1]
        leftOperand = bodyItem[2]
        rightOperand = bodyItem[4]

        for var in self.variables:
            if(var[1] == leftOperand):
                leftOperand = var[2]
            
            if(var[1] == rightOperand):
                rightOperand = var[2]
                
        for var in self.mapped:
            if(var[1] == leftOperand):
                leftOperand = var[2]
            
            if(var[1] == rightOperand):
                rightOperand = var[2]

        operation = bodyItem[3]

        for var in self.variables:
            if(var[1] == varNameToUpdate):
                for func in self.functions:
                    if(func[1] == funcName):
                        if(var[3] == funcName or varNameToUpdate in params):
                            if(var[4] == False or enforceConstant == False):
    
                                left = self.get_left(leftOperand)
                                right = self.get_right(rightOperand)

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

    def get_left(self, leftOperand):
        left = leftOperand

        varObj = None

        for var in self.variables:
            if(var[1] == left):
                varObj = var
                
        if(varObj == None):
            for map in self.mapped:
                if(map[1] == left):
                    varObj = map
                
        if(varObj != None):
            if('"' in varObj[2] or "'" in varObj[2]):
                left = str(varObj[2])
            elif('.' in varObj[2]):
                left = float(varObj[2])
            else:
                left = int(varObj[2])

        return left

    def get_right(self, rightOperand):
        right = rightOperand

        varObj = None

        for var in self.variables:
            if(var[1] == rightOperand):
                varObj = var
                
        if(varObj == None):
            for map in self.mapped:
                if(map[1] == rightOperand):
                    varObj = map
                
        if(varObj != None):
            if('"' in varObj[2] or "'" in varObj[2]):
                right = str(varObj[2])
            elif('.' in varObj[2]):
                right = float(varObj[2])
            else:
                right = int(varObj[2])
                    
        return right
