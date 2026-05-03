from token import *

TYPES = {'int', 'float', 'string', 'double', 'bool', 'char'}
BOOL_SYMS     = {'true', 'false', 'True', 'False'}

class Table:
    def __init__(self):
        # formated as name , type , line
        self.table = {}

    def lookUp(self , name):
        return self.table.get(name)
    
    def allEntries(self):
        return self.table.items()
    def insert(self , name , type , line):
        if name not in self.table:
            self.table[name] = {"type" : type , "line" : line}
    
    def exists(self , name):
        return name in self.table
    
    def __repr__(self):
        result = "name  :: type  :: line\n" 
        for name, info in self.table.items():
            result += name + "   " + info['type'] + "   " + str(info['line']) + "\n"
        return result

def analyze(tokens):
    table = Table()
    errs = []
    i = 0
    n = len(tokens)

    def scanToSemicolon(start):
        j = start
        while j < n and tokens[j].token_type != TOK_SEMICOLON:
            j+=1
        return j
    
    def isBoolSym(tok):
        if tok.token_type == TOK_TRUE or tok.token_type == TOK_FALSE:
            return True
        if tok.token_type == TOK_IDENTIFIER and tok.lexeme in BOOL_SYMS:
            return True
        return False

    def checkRhs(start, end):
        VALID_OPERATORS = {TOK_PLUS, TOK_MINUS, TOK_STAR, TOK_SLASH, TOK_MOD}
        expecting_value = True  

        for j in range(start, end):
            tok = tokens[j]
            
            if expecting_value:
                is_var = (tok.token_type == TOK_IDENTIFIER)
                is_num = (tok.token_type in {TOK_INTEGER, TOK_FLOAT})
                is_bool = isBoolSym(tok)
                
                if is_var or is_num or is_bool:
                    if is_var and not is_bool:
                        # check if it's an actual declared variable
                        if not table.exists(tok.lexeme):
                            errs.append(f"undeclared var : {tok.lexeme} at line : {tok.line}")
                    expecting_value = False
                else:
                    errs.append(f"syntax error at line {tok.line}: expected variable or number, got '{tok.lexeme}'")
            
            else:
                if tok.token_type in VALID_OPERATORS:
                    expecting_value = True
                else:
                    errs.append(f"syntax error at line {tok.line}: expected operator, got '{tok.lexeme}'")
        
        if expecting_value and start < end:
            errs.append(f"incomplete expression at line {tokens[end-1].line}: ends with an operator")

    while i < n :
        tok = tokens[i]
        
        # skip comments
        if tok.token_type in (TOK_SCOMMENT ,TOK_MCOMMENT):
            i+=1
            continue
        
        if tok.token_type == TOK_IDENTIFIER and tok.lexeme in TYPES:
            varType = tok.lexeme
            nameTok =""
            if i + 1 < n :
                nameTok = tokens[i+1]
            else:
                nameTok = None
            
            # int ''
            if nameTok is None or nameTok.token_type != TOK_IDENTIFIER:
                errs.append(f"expected a var name after decl of type : {varType} at line : {tok.line}")
                i+=1
                continue

            # check if var already declared
            existing = table.lookUp(nameTok.lexeme)
            if existing:
                errs.append(
                    f"var '{nameTok.lexeme}' already declared at {nameTok.line}:  "
                    f" on line {existing['line']} as type '{existing['type']}'."
                )
            else:
                table.insert(nameTok.lexeme , varType , nameTok.line)

            # token after name must be = or ;
            if i + 2 < n:
                eq_tok = tokens[i+2]
            else:
                eq_tok = None

            # int i ;
            if eq_tok is not None and eq_tok.token_type == TOK_SEMICOLON:
                i = i + 3
                continue

            # int i = expr ;
            if eq_tok is None or eq_tok.token_type != TOK_ASSIGN:
                errs.append(f"expected '=' after : {nameTok.lexeme} at line : {nameTok.line} and got none !!")

            # now get the semi
            semi = scanToSemicolon(i+3)
            if semi >= n:
                errs.append(f"missing ';' after declaration of '{nameTok.lexeme}' at line : {nameTok.line}")
            if semi == i + 3:
                errs.append(f"expected a value after '=' at line : {nameTok.line}")
            
            checkRhs(i+3 , semi)
            i = semi + 1
            continue

        # assign id = expr
        if tok.token_type == TOK_IDENTIFIER:
            eq_tok = ""
            if i + 1 < n:
                eq_tok = tokens[i+1]
            else:
                eq_tok = None

            if eq_tok is not None and eq_tok.token_type == TOK_ASSIGN:
                if not table.exists(tok.lexeme):
                    errs.append(f"variable : {tok.lexeme}' is used at line : {tok.line} before declaration")

                semi = scanToSemicolon(i + 2)
                if semi >= n:
                    errs.append(f"missing ';' for the var : '{tok.lexeme}' at line : {tok.line}")
                if semi == i + 2:
                    errs.append(f"expected a value after '=' at line : {tok.line}")

                checkRhs(i + 2, semi)
                i = semi + 1
                continue
            
        i+=1

    return table , errs