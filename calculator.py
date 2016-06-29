import sys


INT, FLOAT, PLUS, MINUS, EOF, MUL, DIV, LPAREN, RPAREN = \
     'INT', 'FLOAT', 'PLUS', 'MINUS', 'EOF', 'MUL', 'DIV', 'LPAREN', 'RPAREN'
class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type = self.type, value = self.value)

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.cur_char = self.text[self.pos]

    def error(self):
        raise Exception("Error parse input")

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.cur_char = None
        else:
            self.cur_char = self.text[self.pos]

    def skip(self):
        while self.cur_char is not None and self.cur_char.isspace():
            self.advance()

    def numeric(self):
        ret = ''
        while self.cur_char is not None and self.cur_char.isdigit():
            ret += self.cur_char
            self.advance()

        if self.cur_char is not None and self.cur_char == '.':
            ret += self.cur_char
            self.advance()
            while self.cur_char is not None and self.cur_char.isdigit():
                ret += self.cur_char
                self.advance()
            return FLOAT, float(ret)
            
        return INT, int(ret)

    def last(self):
        pos = self.pos
        pos -= 1
        while pos >= 0 and self.text[pos].isspace():
            pos -= 1
        if pos < 0:
            return None
        else:
            return self.text[pos]

    def next_token(self):
        while self.cur_char is not None:
            if self.cur_char.isspace():
                self.skip()
                continue

            if self.cur_char.isdigit():
                t, v = self.numeric()
                return Token(t, v)

            if self.cur_char == '+':
                if self.pos == 0 or self.last() == '(':
                    self.advance()
                    t, v = self.numeric()
                    token = Token(t, v)
                    return Token(t, token.value)
                self.advance()
                return Token(PLUS, '+')

            if self.cur_char == '-':
                if self.pos == 0 or self.last() == '(':
                    self.advance()
                    t, v = self.numeric()
                    token = Token(t, v)
                    return Token(t, -1 * token.value)
                self.advance()
                return Token(MINUS, '-')

            if self.cur_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.cur_char == '/':
                self.advance()
                return Token(DIV, '*')

            if self.cur_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.cur_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)

class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.cur_token = self.lexer.next_token()

    def error(self):
        raise Exception('Invalid syntax')
        

    def eat(self, token_type):
        if self.cur_token.type == token_type:
            self.cur_token = self.lexer.next_token()
        else:
            self.error()

    def factor(self):
        token = self.cur_token
        if token.type == INT:
            self.eat(INT)
            return token.value
        elif token.type == FLOAT:
            self.eat(FLOAT)
            return token.value
        elif token.type == LPAREN:
            self.eat(LPAREN)
            result = self.expr()
            self.eat(RPAREN)
            return result

    def term(self):
        result = self.factor()
        while self.cur_token.type in (MUL, DIV):
            token = self.cur_token
            if token.type == MUL:
                self.eat(MUL)
                result *= self.factor()
            elif token.type == DIV:
                self.eat(DIV)
                result /= self.factor()
        return result

    def expr(self):

        result = self.term()

        while self.cur_token.type in (PLUS, MINUS):
            token = self.cur_token
            if token.type == PLUS:
                self.eat(PLUS)
                result += self.term()
            elif token.type == MINUS:
                self.eat(MINUS)
                result -= self.term()
                
        return result

def main():
    text = None
    while True:
        try:
            text = raw_input('calc>')
        except:
            print 'end!'
            sys.exit(0)

        if not text:
            continue

        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        ret = interpreter.expr()
        print ret

if __name__ == '__main__':
    main()
