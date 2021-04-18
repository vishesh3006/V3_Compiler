import sys
from lex import *

# Parser object keeps track of current token, checks if the code matches the grammar, and emits code along the way.


func_count = 0
if_count = 0
while_count = 0
funcPossible = 1
class Parser:

    def __init__(self, lexer):
        self.lexer = lexer


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

        while self.checkToken(TokenType.FUNC):
            self.statement()

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program.
        while not self.checkToken(TokenType.EOF):
            self.statement()

        # Check that each label referenced in a GOTO is declared.
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)


    # One of the following statements...
    def statement(self):
        global funcPossible
        global func_count
        global if_count
        global while_count

        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            self.nextToken()
            funcPossible = 0
            if self.checkToken(TokenType.STRING):
                # Simple string, so print it.
                
                # self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken()

            else:
                # Expect an expression and print the result as a float.
                # self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                # self.emitter.emitLine("));")

        # "IF" comparison "THEN" block "ENDIF"
        elif self.checkToken(TokenType.IF):
            if_count += 1
            funcPossible = 0
            self.nextToken()
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()

            # indent += 1
            # Zero or more statements in the body.
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            if_count -= 1

        # "WHILE" comparison "REPEAT" block "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            funcPossible = 0
            while_count += 1
            self.nextToken()
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            while_count -= 1


        # "FUNC" ident "() DO" nl {statement} "ENDFUNC" nl
        elif self.checkToken(TokenType.FUNC):
            
            func_count += 1
            if func_count > 1:
                self.abort("Cannot Declare Function Inside a Function")
            
            if funcPossible == 0:
                self.abort("FUNCTIONS have to be declared at the start of program only")

            funcPossible = 0

            self.nextToken()
            if self.curToken.text in self.funcDeclared:
                self.abort("Function Already Exists: " + self.curToken.text)
            self.funcDeclared.add(self.curToken.text)
            funcName = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.OB)
            arr = []
            while self.checkToken(TokenType.LET):
                self.match(TokenType.LET)
                self.symbols.add(self.curToken.text)
                arr.append(self.curToken.text)
                self.match(TokenType.IDENT)

                if self.checkToken(TokenType.COMMA):
                    self.nextToken()

            
            self.match(TokenType.CB)

            self.match(TokenType.DO)
            self.nl()

            self.funcParams[funcName] = len(arr)
            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDFUNC):
                self.statement()


            for x in arr:
                self.symbols.remove(x)
            self.match(TokenType.ENDFUNC)
            funcPossible = 1
            func_count -= 1

        elif self.checkToken(TokenType.RETURN):
            self.nextToken()


        # "CALL" ident nl
        elif self.checkToken(TokenType.CALL):
            funcPossible = 0
            self.nextToken()

            if self.curToken.text not in self.funcDeclared:
                self.abort("Function Not Declared: " + self.curToken.text)
            funcName = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.OB)
            count = 0
            while self.checkToken(TokenType.IDENT) or self.checkToken(TokenType.NUMBER):
                count += 1
                if self.checkToken(TokenType.IDENT):
                    self.match(TokenType.IDENT)
                else:
                    self.match(TokenType.NUMBER)
                if self.checkToken(TokenType.COMMA):
                    self.nextToken()
            if count != self.funcParams[funcName]:
                self.abort("Invalid Count of Params for Function: " + funcName +" (Required: " + str(self.funcParams[funcName]) +", Received: " + str(count) + ")")
            self.match(TokenType.CB)


        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()
            funcPossible = 0
            # Make sure this label doesn't already exist.
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.match(TokenType.IDENT)

        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            funcPossible = 0
            self.abort("INVALID KEYWORD: GOTO for DESTINATION Language")
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.match(TokenType.IDENT)

        # "LET" ident = expression
        elif self.checkToken(TokenType.LET):
            self.nextToken()
            funcPossible = 0
            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            if self.curToken.text in self.funcDeclared:
                self.abort("INVALID NAME of IDENTIFIER; ALREADY USED for a FUNCTION")

            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            
            self.expression()

        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()
            funcPossible = 0
            # If variable doesn't already exist, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            if self.curToken.text in self.funcDeclared:
                self.abort("INVALID NAME of IDENTIFIER; ALREADY USED for a FUNCTION")

            self.match(TokenType.IDENT)

        # This is not a valid statement. Error!
        else:
            if if_count != 0:
                self.abort("IF not closed with ENDIF")
            elif while_count != 0:
                self.abort("WHILE not closed with ENDWHILE")
            else:
                self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        # Newline.
        self.nl()


    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            # self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            # self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()


    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()
        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            # self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()


    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary()
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            # self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()


    # unary ::= ["+" | "-"] primary
    def unary(self):
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            # self.emitter.emit(self.curToken.text)
            self.nextToken()        
        self.primary()


    # primary ::= number | ident
    def primary(self):
        if self.checkToken(TokenType.NUMBER): 
            # self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            # self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token instead of Number or Identifier")

    # nl ::= '\n'+
    def nl(self):
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

lexer = Lexer(sys.argv[1])
parser = Parser(lexer)
parser.program()