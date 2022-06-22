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

        typeKeywords = ['void', 'number', 'string', 'bool']
        funcKeywords = ['print']
        opKeywords = ['plus', 'minus', 'multiply', 'divide', 'larrow', 'rarrow', 'lbrace', 'rbrace', 'lparen', 'rparen']
        initKeywords = ['initialiser']

        while idx < len(self.tokens):
            if(self.tokens[idx] == 'EOF'):
                break

            if self.tokens[idx] in typeKeywords:
                typeDef = self.tokens[idx]

                if self.tokens[idx + 2] == 'lparen':
                    funcName = self.tokens[idx + 1]
                    funcParams = []
                    currentTok = self.tokens[idx + 3]
                    idx2 = idx + 3
                    paramLength = 0

                    while currentTok != 'rparen':
                        funcParams.append(currentTok)
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
                            elif(currentTok in funcKeywords):
                                funcName2 = currentTok

                                if self.tokens[idx3 + 1] == 'lparen':
                                    funcParams2 = []
                                    currentTok2 = self.tokens[idx3 + 2]
                                    idx4 = idx3 + 2
                                    paramLength2 = 0

                                    while currentTok2 != 'rparen':
                                        funcParams2.append(currentTok2)
                                        idx4 += 1
                                        paramLength2 += 1
                                        currentTok2 = self.tokens[idx4]  

                                    funcBody.append([ 'call function', funcName2, funcParams2 ])  
                                    idx3 += 3 + paramLength2
                                    currentTok = self.tokens[idx3]
                                else:
                                    error('Expected function parameters')

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
                                    
                            bodyLength += 1
                            
                        self.ast.append(['init function', typeDef, funcName, funcParams, funcBody])
                        idx += 7 + paramLength + bodyLength 
            elif self.tokens[idx] not in funcKeywords and self.tokens[idx] not in opKeywords and \
            self.tokens[idx] not in initKeywords and '"' not in self.tokens[idx] and \
            self.tokens[idx] not in '0123456789' and self.tokens[idx + 1] not in ['plus', 'minus', 'multiply', 'divide']:
                funcName3 = self.tokens[idx]

                operators = ['plus', 'minus', 'multiply', 'divide']

                if self.tokens[idx + 1] == 'lparen':
                    funcParams3 = []
                    currentTok3 = self.tokens[idx + 2]
                    idx5 = idx + 2
                    paramLength3 = 0

                    while currentTok3 != 'rparen':
                        funcParams3.append(currentTok3)
                        idx5 += 1
                        paramLength3 += 1
                        currentTok3 = self.tokens[idx5]  

                    self.ast.append([ 'call function', funcName3, funcParams3 ])  
                    idx += 4 + paramLength3

                elif(self.tokens[idx + 1] == 'initialiser'):
                    value1 = self.tokens[idx + 2]
                    identifier = self.tokens[idx + 1]

                    if(self.tokens[idx + 3] in operators):
                        value2 = self.tokens[idx + 4]
                        self.ast.append([ 'assign result of binary operation', identifier, value1, self.tokens[idx + 3], value2 ])
                        idx += 5
                    else:
                        self.ast.append([ 'assignment', identifier, value1 ])
                        idx += 3

            idx += 1

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

