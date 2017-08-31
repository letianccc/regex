from new_regex.regex_data import CharRange
from new_regex.regex_expression import CharsetExpression, AlternateExpression, SequenceExpression, LoopExpression


class Parser(object):
    def __init__(self, regex):
        self.regex = regex
        self.index = 0

    def cur_char(self):
        c = self.regex[self.index]
        self.index += 1
        return c

    def return_char(self):
        self.index -= 1

    def is_char(self, char):
        if self.index < len(self.regex):
            cur_char = self.cur_char()
            if char == cur_char:
                return True
        self.return_char()
        return False

    def is_chars(self, chars):
        if self.index < len(self.regex):
            cur_char = self.cur_char()
            charset = set(chars)
            for char in charset:
                if char == cur_char:
                    return True
        self.return_char()
        return False

    def parse(self):
        return self.parse_expression()

    def parse_expression(self):
        return self.parse_alt()

    def parse_alt(self):
        expr = self.parse_join()
        if self.is_char('|'):
            alt_expr = AlternateExpression()
            alt_expr.left = expr
            alt_expr.right = self.parse_join()
            expr = alt_expr
        return expr

    def parse_join(self):
        expr = self.parse_unit()
        while True:
            right = self.parse_unit()
            if right:
                seq_expr = SequenceExpression()
                seq_expr.left = expr
                seq_expr.right = right
                expr = seq_expr
            else:
                return expr

    def parse_unit(self):
        expr = self.parse_charset()
        if expr:
            loop_expr = self.parse_loop()
            while loop_expr:
                loop_expr.expression = expr
                expr = loop_expr
                loop_expr = self.parse_loop()
        return expr

    def parse_loop(self):
        if self.index == len(self.regex):
            return None

        if self.is_char('*'):
            min = 0
            max = -1
        elif self.is_char('?'):
            min = 0
            max = 1
        elif self.is_char('+'):
            min = 1
            max = -1
        elif self.is_char('{'):
            min = self.num()
            if self.is_char('}'):
                max = min
            elif self.is_char(','):
                if self.is_char('}'):
                    max = -1
                else:
                    max = self.num()
                    if min > max and max != -1:
                        raise Exception("min > max")
                    if not self.is_char('}'):
                        raise Exception("the lack of }")
        else:
            return None

        loop_expr = LoopExpression()
        loop_expr.min = min
        loop_expr.max = max

        return loop_expr

    def parse_charset(self):
        if self.index == len(self.regex):
            return None
        if self.is_char('\\'):
            expr = self.expr_for_escape()
        elif self.is_char('('):
            expr = self.parse_expression()
            if not self.is_char(')'):
                raise Exception("parse_charset: the lack of )")
        elif self.is_char('['):
            expr = self.expr_for_square_bracket()
        elif self.is_chars('|*+?()'):
            self.return_char()
            return None
        else:
            expr = CharsetExpression()
            c = self.cur_char()
            expr.add_range(CharRange(c, c))

        return expr

    def expr_for_escape(self):
        chars = {'[', ']', '(', ')', '\\', '\"', '\'', '+', '*', '?', '|', '.'}
        expr = CharsetExpression()
        c = self.cur_char()

        if c == 'r':
            expr.add_range(CharRange('\r', '\r'))
        elif c == 'n':
            expr.add_range(CharRange('\n', '\n'))
        elif c == 't':
            expr.add_range(CharRange('\t', '\t'))
        elif c in chars:
            expr.add_range(CharRange(c, c))
        elif c == 'd' or c == 'D':
            expr.reverse = (True if c == 'D' else False)
            expr.add_range(CharRange('0', '9'))
        elif c == 's' or c == 'S':
            expr.reverse = (True if c == 'S' else False)
            expr.add_range(CharRange(' ', ' '))
            expr.add_range(CharRange('\r', '\r'))
            expr.add_range(CharRange('\n', '\n'))
            expr.add_range(CharRange('\t', '\t'))
        elif c == 'w' or c == 'W':
            expr.reverse = (True if c == 'W' else False)
            expr.add_range(CharRange('_', '_'))
            expr.add_range(CharRange('a', 'z'))
            expr.add_range(CharRange('A', 'Z'))
            expr.add_range(CharRange('0', '9'))
        else:
            raise Exception("parse_charset: wrong escape char")

        return expr

    def expr_for_square_bracket(self):
        expr = CharsetExpression()
        if self.is_char('^'):
            expr.reverse = True
        if self.is_char(']'):
            raise Exception("parse_charset: wrong []")

        while True:
            if self.is_char('\\'):
                c = self.cur_char()
                if c == 'r':
                    a = '\r'
                elif c == 'n':
                    a = '\n'
                elif c == 't':
                    a = '\t'
                else:
                    a = c
                b = a
            else:
                a = self.cur_char()
                if self.is_char('-'):
                    b = self.cur_char()
                    if not (a.isalpha() and b.isalpha()):
                        if not (a.isdigit() and b.isdigit()):
                            raise Exception("parse_charset: wrong [a-b]")
                else:
                    b = a

            r = CharRange(a, b)
            expr.add_range_with_conflict(r)
            if self.is_char(']'):
                break

        return expr

    def num(self):
        num = 0
        while True:
            c = self.cur_char()
            if not c.isdigit():
                break
            num = num * 10 + int(c)
        self.return_char()
        return num




