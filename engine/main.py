from wdscript import WaldenScript
from interpreter import Interpreter

import sys

def main():
    script = WaldenScript()
    ast = script.read(sys.argv[1])

    interpreter = Interpreter()
    interpreter.interpret(ast)
   
main()