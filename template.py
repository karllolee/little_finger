"""
{{username}}

{% if cond %}
{% endif %}

{% for i in list%}
{% endfor %}

{# comment #}

expression

call

"""

class Token(object):
    LITERAL = 'LITERAL'
    VARIABLE = 'VARIABLE'
    LOOP = 'LOOP'
    CONDITION = 'CONDITION'
    COMMENT = 'COMMENT'
    ENDFOR = "ENDFOR"
    ENDIF = "ENDIF"
    EOF = 'EOF'
    
    def __init__(self, type = None, value = None):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token(%s, %s)" % (self.type, self.value)

class Tokenizer(object):
    def __init__(self, text):
        if not isinstance(text, str):
            raise Exception("text type must be str")
        self.text = text
        self.pos = 0

    def error(self):
        raise Exception("tokenize failed")

    def eof(self):
        return self.pos >= len(self.text)

    def advance(self):
        self.pos += 1

    def skip(self):
        while not self.eof() and self.text[self.pos] == ' ':
            self.advance()

    def get_word(self):
        self.skip()
        last_pos = self.pos
        while not self.eof() and self.text[self.pos] != ' ':
            self.advance()
        if last_pos == self.pos:
            self.error()
        return self.text[last_pos:self.pos]

    def get_loop_or_cond(self):
        self.skip()
        last_pos = self.pos
        while not self.eof():
            if self.text[self.pos] != '%':
                self.advance()
            else:
                self.advance()
                if not self.eof() and self.text[self.pos] == '}':
                    return self.text[last_pos:(self.pos - 1)]
        self.error()

    def get_comment(self):
        self.skip()
        last_pos = self.pos
        while not self.eof():
            if self.text[self.pos] != '#':
                self.advance()
            else:
                self.advance()
                if not self.eof() and self.text[self.pos] == '}':
                    return

        self.error()

    def get_variable(self):
        self.skip()
        last_pos = self.pos
        while not self.eof():
            if self.text[self.pos] != '}':
                self.advance()
            else:
                self.advance()
                if not self.eof() and self.text[self.pos] == '}':
                    return self.text[last_pos:(self.pos - 1)]
        self.error()

    def get_end_loop_or_cond(self):
        self.skip()
        if not self.eof() and self.text[self.pos] == '%':
            self.advance()
        
        if not self.eof() and self.text[self.pos] == '}':
            return
        self.error()

    def next_char(self):
        pos = self.pos + 1
        if pos < len(self.text):
            return self.text[pos]
        else:
            return None
        
    def next(self):
        last_pos = self.pos
        while not self.eof():
            if self.text[self.pos] != '{':
                self.advance()
                continue
            else:
                c = self.next_char()
                if c == '%' or c == '{' or c == '#':
                    if last_pos != self.pos:
                        return Token(Token.LITERAL, self.text[last_pos:self.pos])
                    self.advance()         
                    if not self.eof():
                        self.advance()
                        if c == '%':
                            w = self.get_word()
                            
                            if w == 'for':
                                value = self.get_loop_or_cond()
                                self.advance()
                                return Token(Token.LOOP, value)
                            elif w == 'if':
                                value = self.get_loop_or_cond()
                                self.advance()
                                return Token(Token.CONDITION, value)
                            elif w == 'endfor':
                                self.get_end_loop_or_cond()
                                self.advance()
                                return Token(Token.ENDFOR, "endfor")
                            elif w == 'endif':
                                self.get_end_loop_or_cond()
                                self.advance()
                                return Token(Token.ENDIF, "endif")
                            else:
                                self.error()
                        elif c == '{':
                            value = self.get_variable()
                            self.advance()
                            return Token(Token.VARIABLE, value)
                        else:
                            self.get_comment()
                            self.advance()
                            return self.next()
                else:
                    self.advance()
                    continue
                
        if self.eof():
            if last_pos == self.pos:
                return Token(Token.EOF)
            else:
                return Token(Token.LITERAL, self.text[(last_pos):])

        self.error()


class Template(object):
    result = 'result'
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
        self.ctx = {}

        self.level = 0

    def error(self):
        raise Exception("template rules not correct")

    def add_string_line(self, value):
        indent = self.level * '    '
        return '%s%s += """%s"""' % (indent, Template.result, value)
    
    def add_variable_line(self, value):
        indent = self.level * '    '
        return '%s%s += str(%s)' % (indent, Template.result, value)

    def add_code_line(self, value):
        indent = self.level * '    '
        return '%s%s' % (indent, value)

    def for_block_begin(self, value):
        return 'for %s :' % value

    def if_block_begin(self, value):
        return 'if %s :' % value

    def handle(self):
        for_cnt = 0
        if_cnt = 0
        result = []
        result.append("%s = ''" % Template.result)
        
        token = self.tokenizer.next()
        while token.type != Token.EOF:
            if token.type == Token.LITERAL:
                e = self.add_string_line(token.value)
                result.append(e)
            elif token.type == Token.VARIABLE:
                e = self.add_variable_line(token.value)
                result.append(e)
            elif token.type == Token.CONDITION:
                e = self.add_code_line(self.if_block_begin(token.value))
                result.append(e)
                if_cnt += 1
                self.level += 1
            elif token.type == Token.LOOP:
                e = self.add_code_line(self.for_block_begin(token.value))
                result.append(e)
                self.level += 1
                for_cnt += 1
            elif token.type == Token.ENDFOR:
                self.level -= 1
                for_cnt -= 1
            elif token.type == Token.ENDIF:
                self.level -= 1
                if_cnt -= 1
            else:
                self.error()

            token = self.tokenizer.next()

        if for_cnt != 0 or if_cnt != 0:
            self.error()

        return result

    def render(self, **kwargs):
        self.ctx = kwargs
        result = self.handle()
        expr =  '\n'.join(result)
        
        exec(expr, {}, self.ctx)
        
        return self.ctx[Template.result]
        
if __name__ == "__main__":
    text = """    <p>Products:</p>
<ul>
{% for product in product_list   %}
    <li>   {{ product }} </li>
    {% for i  in inner %}
        <p>hello {{result}} world</p>
    {% endfor %}
{%   endfor   %}
     </ul>

   {% if user %}
    <p> Welcome, {{ user }}!</p>
{# test hello world #}
{% endif %}"""

    t = Template(text)
    print t.render(product_list = [1,2], user = True, inner = [5, 6])




            
                
            
        

        
            
        
        
        

