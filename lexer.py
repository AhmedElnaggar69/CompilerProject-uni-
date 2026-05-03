from token import *
numsContainer = ['0','1','2','3','4','5','6','7','8','9']
KEYWORDS = {
    "if": TOK_IF,
    "then": TOK_THEN,
    "else": TOK_ELSE,
    "true": TOK_TRUE,
    "false": TOK_FALSE,
    "and": TOK_AND,
    "or": TOK_OR,
    "while": TOK_WHILE,
    "do": TOK_DO,
    "for": TOK_FOR,
    "func": TOK_FUNC,
    "null": TOK_NULL,
    "end": TOK_END,
    "print": TOK_PRINT,
    "println": TOK_PRINTLN,
    "return": TOK_RET
}
class lexer:
    def __init__(self , src):
        self.tokens = []
        self.curr = 0 
        self.start = 0
        self.src = src
        self.line = 1

    def add_token(self , tokenType):
        self.tokens.append(token(tokenType , self.src[self.start:self.curr] , self.line))
    def tokenize(self):
        # scan tokens from the src and add them to the list
        while(self.curr < len(self.src)):
            self.start = self.curr
            char = self.advance()

            if char == '\n':
                self.line = self.line + 1
            elif char == '\t':
                pass
            elif char == '\r':
                pass
            elif char == ' ':
                pass         
            elif char == '+':
                self.add_token(TOK_PLUS)

            elif char == '-':
                self.add_token(TOK_MINUS)

            elif char == '*':
                self.add_token(TOK_STAR)

            elif char == '/':
                self.add_token(TOK_SLASH)

            elif char == '^':
                self.add_token(TOK_CARET)

            elif char == '%':
                self.add_token(TOK_MOD)

            elif char == '(':
                self.add_token(TOK_LPAREN)

            elif char == ')':
                self.add_token(TOK_RPAREN)

            elif char == '{':
                self.add_token(TOK_LCURLY)

            elif char == '}':
                self.add_token(TOK_RCURLY)

            elif char == '[':
                self.add_token(TOK_LSQUAR)

            elif char == ']':
                self.add_token(TOK_RSQUAR)

            elif char == ',':
                self.add_token(TOK_COMMA)

            elif char == '.':
                self.add_token(TOK_DOT)

            elif char == ':':
                self.add_token(TOK_COLON)

            elif char == ';':
                self.add_token(TOK_SEMICOLON)

            elif char == '?':
                self.add_token(TOK_QUESTION)

            elif char == '=':
                if self.match('='):
                    self.add_token(TOK_EQ)
                else:
                    self.add_token(TOK_ASSIGN)

            elif char == '!':
                if self.match('='):
                    self.add_token(TOK_NE)
                else :
                    self.add_token(TOK_NOT)


            elif char == '>':
                if self.match('='):
                    self.add_token(TOK_GE)
                elif self.match('>'):
                    self.add_token(TOK_GTGT)
                else:
                    self.add_token(TOK_GT)



            elif char == '<':
                if self.match('='):
                    self.add_token(TOK_LE)
                elif self.match('<'):
                    self.add_token(TOK_LTLT)
                else:
                    self.add_token(TOK_LT)
            

        
            elif char == '$' and self.look_forward()=="$":
                print(char + ' ' + self.look_forward())
            
            # todo (ints and float parser)
            self.NumberTokenizer(char=char)
            self.stringParser(char=char , sign='"')
            self.stringParser(char=char , sign="'")
            self.IdParser(char=char)
            self.commentsParser(char=char)
            # todo : check if it starts with "" or '' and get the string token
            # todo : apha chars (a letter) or identifier

        return self.tokens
    

    def NumberTokenizer(self,char):
        
        if char in numsContainer:
            IsFloat = False
            while(self.look() in numsContainer):
                self.advance()
            if self.look() == '.' and self.look_forward() in numsContainer:
                IsFloat = True
                self.advance()
                while self.look() in numsContainer:
                    self.advance()
            if IsFloat:
                self.add_token(TOK_FLOAT)
            else:
                self.add_token(TOK_INTEGER)


        
    def IdParser(self , char):
        if char.isalpha() or char=='_':
            while self.curr < len(self.src) and ( self.look().isalnum() or self.look() == '_' ):
                self.advance()
            subString = self.src[self.start:self.curr]
            keyType = KEYWORDS.get(subString)
            if subString in KEYWORDS:
                self.add_token(keyType)
            else:
                self.add_token(TOK_IDENTIFIER)
    
    def stringParser(self , char , sign):
        if char==sign:
            self.start = self.curr
            while self.look() != sign and not self.curr >= len(self.src):
               self.advance();
            

            # if we reached the end of the src file scaning for the end of the string without finding the closing '/"
            if self.curr >= len(self.src):
                raise SystemError("reached the end of the file scaning for a closing sign for a string")
            

            self.add_token(TOK_STRING)
            self.advance();
    
    def commentsParser(self , char):
        if char == '$':
            if self.match('$'):  
                self.start = self.curr 
                while(self.curr < len(self.src)):
                    if self.look() =='$' and self.look_forward() =='$':
                        break
                    elif self.look() =='\n':
                        self.line+=1
                    self.advance()
                self.add_token(TOK_MCOMMENT)
                self.advance()
                self.advance()
            else:
                while self.look() != '\n' and self.curr < len(self.src):
                    self.advance()
                self.add_token(TOK_SCOMMENT)
            

    def advance(self):
        if self.curr >= len(self.src):
            return False
        
        
        char = self.src[self.curr]
        self.curr = self.curr + 1
        return char
    

    def look(self):
        if self.curr >= len(self.src):
            return False
        
        return self.src[self.curr]
    
    
    def look_forward(self , n=1):
        if self.curr + 1 >= len(self.src):
            return False
        
        if self.curr >= len(self.src):
            return '\0'
        return self.src[self.curr + n]
    
    
    def match(self , expected):
        if self.curr >= len(self.src):
            return False
        if self.src[self.curr] != expected:
            return False
        self.curr = self.curr + 1
        return True

