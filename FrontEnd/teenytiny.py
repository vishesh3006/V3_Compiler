from lex import *
from emit import *
import parse
import parser_java
import parser_cpp
import parser_py
import sys



def main():
    # print("V3 Compiler")

    # if len(sys.argv) != 2:
    #     sys.exit("Error: Compiler needs source file as argument.")
    with open("hello.tiny", 'r', encoding='utf-8') as inputFile:
        it = inputFile.read()
            
    
    lexer = Lexer(it)
    lang = sys.argv[1]
    # print(lang)

    if lang == 'C':
        emitter = Emitter("out.c")
        parser = parse.Parser(lexer, emitter)
        parser.program() # Start the parser.
        emitter.writeFile() # Write the output to file.

    elif lang == 'C++':
        emitter = Emitter("out.cpp")
        parser = parser_cpp.Parser(lexer, emitter)
        parser.program() # Start the parser.
        emitter.writeFile() # Write the output to file.

    elif lang == 'Java':
        emitter = Emitter("out.java")
        parser = parser_java.Parser(lexer, emitter)
        parser.program() # Start the parser.
        emitter.writeFile() # Write the output to file.
    
    elif lang == 'Python':
        emitter = Emitter("out.py")
        parser = parser_py.Parser(lexer, emitter)
        parser.program() # Start the parser.
        emitter.writeFile() # Write the output to file.

    print("Result: Compiling Completed")

main()
