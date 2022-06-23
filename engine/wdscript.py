
typeKeywords = ['void', 'number', 'string', 'bool']
funcKeywords = ['out']
opKeywords = ['plus', 'minus', 'multiply', 'divide', 'larrow', 'rarrow', 'lbrace', 'rbrace', 'lparen', 'rparen']
initKeywords = ['initialiser']

class WaldenScript:
    def __init__(self):
        self.index = -1
        self.tokens = []
        self.ast = []
        self.filename = None
        self.file = None
        self.current = None

    def advance(self):
        self.index += 1

        if(self.index >= len(self.uIn)):
            self.current = '<EOF>'
        else:
            self.current = self.uIn[self.index]

    def read(self, filename):
        self.filename = filename

        file = open(filename, 'r')
        self.uIn = file.read()
        file.close()

        self.build_tokens()
        self.build_ast()

        return self.ast

    def build_tokens(self):
        if(self.uIn == ''):
            return

        self.advance()

        while(self.index < len(self.uIn)):
            if(self.current == '<EOF>'):
                break

            if(self.current == '#'): # comment
                while(self.current != '\n'):
                    self.advance()

            if(self.current in ' \t\n'):
                self.advance()
            elif(self.current == '+'):
                self.tokens.append('plus')
                self.advance()
            elif(self.current == '-'):
                self.advance()

                if self.current == '>':
                    self.tokens.append('initialiser')
                    self.advance()
                else:
                    self.tokens.append('minus')

            elif(self.current == '*'):
                self.tokens.append('multiply')
                self.advance()
            elif(self.current == '/'):
                self.tokens.append('divide')
                self.advance()
            elif(self.current == '('):
                self.tokens.append('lparen')
                self.advance()
            elif(self.current == ')'):
                self.tokens.append('rparen')
                self.advance()
            elif(self.current == '<'):
                self.tokens.append('larrow')
                self.advance()
            elif(self.current == '>'):
                self.tokens.append('rarrow')
                self.advance()
            elif(self.current == '{'):
                self.tokens.append('lbrace')
                self.advance()
            elif(self.current == '}'):
                self.tokens.append('rbrace')
                self.advance()
            elif(self.current == ','):
                self.tokens.append('comma')
                self.advance()
            elif(self.current == '"' or self.current == "'"):
                self.make_string()
            elif(self.current in '0123456789'):
                self.make_number()
            elif(self.current in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
                self.make_letter()
            else:
                print('Unexpected character: ' + self.current)
                self.advance()
        
        self.tokens.append('EOF')

    def build_ast(self):
        if(self.tokens == []):
            return

        idx = 0

        while idx < len(self.tokens):
            if(self.tokens[idx] == 'EOF'):
                break

            if self.tokens[idx] in typeKeywords : #bug HEERREEE
                idx += self.make_from_type(idx) 

    def make_string(self):
        string = ''
        self.advance()
        
        while(self.current != '"' and self.current != "'"):
            string += self.current
            self.advance()

        self.tokens.append('"' + string + '"')
        self.advance()
            
    def make_number(self):
        number = ''
        while(self.current in '0123456789'):
            number += self.current
            self.advance()

        if(self.current == '.'):
            number += '.'
            self.advance()

            while(self.current in '0123456789'):
                number += self.current
                self.advance()

        self.tokens.append(number)

    def make_letter(self):
        letter = ''
        while(self.current in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            letter += self.current
            self.advance()

        self.tokens.append(letter)
    
    def make_variable(self, currentTok, idx3, funcBody):
        newTypeDef = currentTok

        if(self.tokens[idx3 + 2] == 'initialiser'):
            varName = self.tokens[idx3 + 1]
            value = self.tokens[idx3 + 3]

            funcBody.append([ 'init variable', newTypeDef, varName, value ])    
            idx3 += 4
            currentTok = self.tokens[idx3]

        else:
            varName = self.tokens[idx3 + 1]
            funcBody.append([ 'init variable', newTypeDef, varName, 'none' ])   
            idx3 += 2
            currentTok = self.tokens[idx3]

        return (currentTok, idx3, funcBody)

    def call_function(self, currentTok, idx3, funcBody):
        funcName2 = currentTok

        if self.tokens[idx3 + 1] == 'lparen':
            funcParams2 = []
            currentTok2 = self.tokens[idx3 + 2]
            idx4 = idx3 + 2
            paramLength2 = 0

            while currentTok2 != 'rparen':
                if(currentTok2 != 'comma'):
                    funcParams2.append(currentTok2)
                    idx4 += 1
                    paramLength2 += 1
                    currentTok2 = self.tokens[idx4]  
                else:
                    idx4 += 1
                    paramLength2 += 1
                    currentTok2 = self.tokens[idx4]  

            funcBody.append([ 'call function', funcName2, funcParams2 ])  
            idx3 += 3 + paramLength2
            currentTok = self.tokens[idx3]
        else:
            print('Expected function parameters')

        return (currentTok, idx3, funcBody)

    def make_from_type(self, idx):
        typeDef = self.tokens[idx]

        if self.tokens[idx + 2] == 'lparen':
            funcName = self.tokens[idx + 1]
            funcParams = []
            currentTok = self.tokens[idx + 3]
            idx2 = idx + 3
            paramLength = 0

            while currentTok != 'rparen':
                if(currentTok != 'comma'):
                    funcParams.append(currentTok)
                    idx2 += 1
                    paramLength += 1
                    currentTok = self.tokens[idx2]    
                else:
                    idx2 += 1
                    paramLength += 1
                    currentTok = self.tokens[idx2]    

            # declared function
            if self.tokens[idx + 4 + paramLength] == 'initialiser':
                funcBody = []
                currentTok = self.tokens[idx + 6 + paramLength]
                idx3 = idx + 6 + paramLength
                bodyLength = 0

                while currentTok != 'rbrace':
                    if(currentTok == 'EOF'):
                        break

                    if(currentTok in typeKeywords):
                        (newCurrentTok, newIdx3, newFuncBody) = self.make_variable(currentTok, idx3, funcBody)

                        currentTok = newCurrentTok
                        idx3 = newIdx3
                        funcBody = newFuncBody
                        
                    elif(currentTok in funcKeywords):
                        (newCurrentTok, newIdx3, newFuncBody) = self.call_function(currentTok, idx3, funcBody)

                        currentTok = newCurrentTok
                        idx3 = newIdx3
                        funcBody = newFuncBody

                    else:
                        identifier = currentTok
                        
                        if(self.tokens[idx3 + 1] == 'initialiser'):
                            value1 = self.tokens[idx3 + 2]

                            operators = ['plus', 'minus', 'multiply', 'divide']
                            if(self.tokens[idx3 + 3] in operators):
                                value2 = self.tokens[idx3 + 4]
                                funcBody.append([ 'assign result of binary operation', identifier, value1, self.tokens[idx3 + 3], value2 ])
                                idx3 += 5
                                currentTok = self.tokens[idx3]
                            else:
                                funcBody.append([ 'assignment', identifier, value1 ])
                                idx3 += 3
                                currentTok = self.tokens[idx3]
                        else:
                            (newCurrentTok, newIdx3, newFuncBody) = self.call_function(currentTok, idx3, funcBody)

                            currentTok = newCurrentTok
                            idx3 = newIdx3
                            funcBody = newFuncBody

                            
                    bodyLength += 1
                    
                self.ast.append(['init function', typeDef, funcName, funcParams, funcBody])
                idx += idx3 + 1      

        return idx       