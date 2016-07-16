import sys

INT, ADD, SUB, MUL, DIV, LP, RP = 'INT', 'ADD', 'SUB', 'MUL', 'DIV', 'LP', 'RP'

class Token(object):
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token(%s, "%s")' % (self.type, self.value)

class Tokenizer(object):
    def __init__(self, text):
        self.text = text
        if len(self.text) == 0:
            self.pos = 1
        else:
            self.pos = 0

    def skip(self):
        while not self.eof() and self.text[self.pos] == ' ':
            self.advance()

    def advance(self):
        self.pos += 1
        
    def eof(self):
        if self.pos >= len(self.text):
            return True
        else:
            return False

    def numeric(self):
        v = ''
        while not self.eof() and str.isdigit(self.text[self.pos]):
            v += self.text[self.pos]
            self.advance()
        return int(v)

    def next(self):
        self.skip()
        if not self.eof():
            c = self.text[self.pos]
            if str.isdigit(c):
                v = self.numeric()
                return Token(INT, v)
            elif c == '+':
                self.advance()
                return Token(ADD, '+')
            elif c == '-':
                self.advance()
                return Token(SUB, '-')
            elif c == '*':
                self.advance()
                return Token(MUL, '*')
            elif c == '/':
                self.advance()
                return Token(DIV, '/')
            elif c == '(':
                self.advance()
                return Token(LP, '(')
            elif c == ')':
                self.advance()
                return Token(RP, ')')
            else:
                sys.exit(1)
                
        return None

def rnp(text):
    stack = []
    ret = []
    op_pri = {LP:3, RP:0, MUL:1, DIV:1, ADD:2, SUB:2}
    tn = Tokenizer(text)
    t = tn.next()
    while t is not None:
        if t.type == INT:
            ret.append(t)
        elif t.type == LP:
            stack.append(t)
        elif t.type == RP:
            flag = False
            while len(stack) > 0:
                v = stack.pop()
                if v.type != LP:
                    ret.append(v)
                    flag = True
                else:
                    break
            if not flag:
                print 'not correct text'
                sys.exit(1)
        elif t.type in (ADD, SUB, MUL, DIV):
            if len(stack) == 0:
                stack.append(t)
            else:
                top = stack[len(stack) -1]
                while op_pri[top.type] <= op_pri[t.type]:
                    ret.append(top)
                    stack.pop()
                    if len(stack) != 0:
                        top = stack[len(stack) -1]
                    else:
                        break
                stack.append(t)
        else:
            print 'not correcnt type'
            sys.exit(1)
        t = tn.next()
    while len(stack) != 0:
        ret.append(stack.pop())
    return ret

def calculate(text):
    rnp_list = rnp(text)
    stack = []
    for t in rnp_list:
        if t.type == INT:
            stack.append(t.value)
        elif t.type == ADD:
            if len(stack) < 2:
                print "not correct text"
                sys.exit(1)
            l = stack.pop()
            r = stack.pop()
            stack.append(r + l)
        elif t.type == SUB:
            if len(stack) < 2:
                sys.exit(1)
            l = stack.pop()
            r = stack.pop()
            stack.append(r - l)
        elif t.type == MUL:
            if len(stack) < 2:
                sys.exit(1)
            l = stack.pop()
            r = stack.pop()
            stack.append(r * l)
        elif t.type == DIV:
            if len(stack) < 2:
                sys.exit(1)
            l = stack.pop()
            r = stack.pop()
            stack.append(r / l)
        else:
            print "not correct text"
            sys.exit(1)
    if len(stack) != 1:
        print "not correct text"
    return stack[0]
    
if __name__ == "__main__":

    text = "1 + 4 * (2 - 3)"
    print [t.value for t in rnp(text)]
    print calculate(text)
    print eval(text)

        

    
    
    
