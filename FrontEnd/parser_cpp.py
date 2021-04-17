import sys
from lex import *

# Parser object keeps track of current token, checks if the code matches the grammar, and emits code along the way.
indent = 0

class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()    # All variables we have declared so far.
        self.labelsDeclared = set() # Keep track of all labels declared
        self.labelsGotoed = set() # All labels goto'ed, so we know if they exist or not.
        self.funcDeclared = set() # ALL functions
        self.funcParams = {}

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()    # Call this twice to initialize current and peek.

    # Return true if the current token matches.
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Return true if the next token matches.
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances the current token.
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # No need to worry about passing the EOF, lexer handles that.

    # Return true if the current token is a comparison operator.
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    def abort(self, message):
        print("Error! " + message)
        sys.exit()


    # Production rules.

    # program ::= {statement}
    def program(self):
        global indent
        self.emitter.headerLine("#include <iostream>")
        self.emitter.headerLine("using namespace std;")
        while self.checkToken(TokenType.FUNC):
            self.statement()
        self.emitter.emitLine("int main(){")
        indent += 1
        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program.
        while not self.checkToken(TokenType.EOF):
            self.statement()

        # Wrap things up.
        for i in range(indent):
                self.emitter.emit('    ')
        self.emitter.emitLine("return 0;")
        indent -= 1
        self.emitter.emitLine("}")

        # Check that each label referenced in a GOTO is declared.
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)


    # One of the following statements...
    def statement(self):
        # Check the first token to see what kind of statement this is.
        global indent
        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # Simple string, so print it.
                for i in range(indent):
                    self.emitter.emit('    ')
                self.emitter.emitLine("std::cout << \"" + self.curToken.text + "\"<<endl;")
                self.nextToken()

            else:
                # Expect an expression and print the result as a float.
                for i in range(indent):
                    self.emitter.emit('    ')
                self.emitter.emit("std::cout << ")
                self.expression()
                self.emitter.emitLine("<<endl;")

        # "IF" comparison "THEN" block "ENDIF"
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")
            indent += 1
            # Zero or more statements in the body.
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            indent -= 1
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emitLine("}")
            
        # "WHILE" comparison "REPEAT" block "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")
            indent += 1
            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            indent -= 1
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emitLine("}")

        # "FUNC" ident "() DO" nl {statement} "ENDFUNC" nl
        elif self.checkToken(TokenType.FUNC):
            self.emitter.emit("void ")

            self.nextToken()
            if self.curToken.text in self.funcDeclared:
                self.abort("FUNC already exists: " + self.curToken.text)
            self.funcDeclared.add(self.curToken.text)
            funcName = self.curToken.text
            self.emitter.emit(self.curToken.text + "(")
            self.match(TokenType.IDENT)
            self.match(TokenType.OB)
            arr = []
            while self.checkToken(TokenType.LET):
                self.match(TokenType.LET)
                self.emitter.emit("float " + self.curToken.text)
                self.symbols.add(self.curToken.text)
                arr.append(self.curToken.text)
                self.match(TokenType.IDENT)

                if self.checkToken(TokenType.COMMA):
                    self.emitter.emit(", ")
                    self.nextToken()

            self.emitter.emitLine("){")
            indent += 1
            self.match(TokenType.CB)

            self.match(TokenType.DO)
            self.nl()

            self.funcParams[funcName] = len(arr)
            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDFUNC):
                self.statement()


            for x in arr:
                self.symbols.remove(x)
            
            indent -= 1
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emitLine("}")
            self.match(TokenType.ENDFUNC)

        elif self.checkToken(TokenType.RETURN):
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emitLine("return;")
            self.nextToken()


        # "CALL" ident nl
        elif self.checkToken(TokenType.CALL):

            self.nextToken()
            if self.curToken.text not in self.funcDeclared:
                self.abort("Function not declared: " + self.curToken.text)
            funcName = self.curToken.text
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emit(self.curToken.text + "(")
            self.match(TokenType.IDENT)
            self.match(TokenType.OB)
            count = 0
            while self.checkToken(TokenType.IDENT) or self.checkToken(TokenType.NUMBER):
                count += 1
                if self.checkToken(TokenType.IDENT):
                    self.emitter.emit(self.curToken.text)
                    self.match(TokenType.IDENT)
                else:
                    self.emitter.emit(self.curToken.text)
                    self.match(TokenType.NUMBER)
                if self.checkToken(TokenType.COMMA):
                    self.emitter.emit(", ")
                    self.nextToken()
            if count != self.funcParams[funcName]:
                self.abort("Invalid count of params for Function: " + funcName +" Required: " + str(self.funcParams[funcName]) +" received: " + str(count))
            self.emitter.emitLine(");")
            self.match(TokenType.CB)


        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()
            for i in range(indent):
                self.emitter.emit('    ')
            # Make sure this label doesn't already exist.
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        # "LET" ident = expression
        elif self.checkToken(TokenType.LET):
            self.nextToken()
            for i in range(indent):
                self.emitter.emit('    ')
            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.emitLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emitLine(";")



        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()

            
            # If variable doesn't already exist, declare it.
            if self.curToken.text not in self.symbols:
                for i in range(indent):
                    self.emitter.emit('    ')
                self.symbols.add(self.curToken.text)
                self.emitter.emitLine("float " + self.curToken.text + ";")

            # Emit scanf but also validate the input. If invalid, set the variable to 0 and clear the input.
            # self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            for i in range(indent):
                self.emitter.emit('    ')
            self.emitter.emitLine("std::cin >> " + self.curToken.text +";")
            self.match(TokenType.IDENT)

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        # Newline.
        self.nl()


    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()


    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()
        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()


    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary()
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()


    # unary ::= ["+" | "-"] primary
    def unary(self):
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()


    # primary ::= number | ident
    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
