from new_regex.regex_automation import Automation, EpsilonNfa, State
from new_regex.regex_expression import CharsetExpression, AlternateExpression, SequenceExpression, LoopExpression
from new_regex.regex_data import CharRange
from copy import deepcopy
from functools import cmp_to_key


class Algorithm(object):
    pass


class NormalizeAlgorithm(Algorithm):
    def loop(self, charset_expr, char_ranges):
        if charset_expr.reverse:
            begin = 1
            char_ranges.sort(key=cmp_to_key(sort_func))

            for r in char_ranges:
                if ord(r.begin) > begin:
                    char_range = CharRange(chr(begin), prior_char(r.begin))
                    self.process(charset_expr, char_range)
                    begin = ord(r.end) + 1
            if begin <= 65535:
                char_range = CharRange(chr(begin), chr(65535))
                self.process(charset_expr, char_range)

        else:
            for r in char_ranges:
                self.process(charset_expr, r)

    def apply(self, expr):
        expr_type = expr.__class__
        func_dict = {SequenceExpression:   self.seq_apply,
                     AlternateExpression:  self.alt_apply,
                     LoopExpression:       self.loop_apply,
                     CharsetExpression:    self.charset_apply}
        func = func_dict[expr_type]
        func(expr)

    def seq_apply(self, expr):
        self.apply(expr.left)
        self.apply(expr.right)

    def alt_apply(self, expr):
        self.apply(expr.left)
        self.apply(expr.right)

    def loop_apply(self, expr):
        self.apply(expr.expression)


class BuildNormalizedCharSetAlgorithm(NormalizeAlgorithm):
    def __init__(self):
        self.target = list()

    def charset_apply(self, expr):
        self.loop(expr, expr.ranges)

    def process(self, charset_expr, char_range):
        target = self.target
        b = char_range.begin
        e = char_range.end
        index = 0

        while index < len(target):
            cur = target[index]
            if cur.end < b or cur.begin > e:
                index += 1
            elif cur.begin < b:
                # range   :      [    ?
                # current :   [     ]
                target.remove(cur)
                r = CharRange(cur.begin, prior_char(b))
                target.append(r)
                r = CharRange(b, cur.end)
                target.append(r)
                target.sort(key=cmp_to_key(sort_func))
                index += 1
            elif cur.begin > b:
                # range   :  [      ]
                # current :     [   ?
                r = CharRange(b, prior_char(cur.begin))
                target.append(r)
                b = cur.begin
            elif cur.end < e:
                # range   :  [         ]
                # current :  [     ]
                b = next_char(cur.end)
                index += 1
            elif cur.end > e:
                # range   :  [   ]
                # current :  [      ]
                target.remove(cur)
                r = CharRange(b, e)
                target.append(r)
                r = CharRange(next_char(e), cur.end)
                target.append(r)
                target.sort(key=cmp_to_key(sort_func))
                return
            else:
                # range   :  [   ]
                # current :  [   ]
                return
        target.append(CharRange(b, e))
        target.sort(key=cmp_to_key(sort_func))


class SetNormalizedCharSetAlgorithm(NormalizeAlgorithm):
    def __init__(self, normalized_charset):
        self.target = normalized_charset

    def charset_apply(self, expr):
        ranges = deepcopy(expr.ranges)
        expr.ranges.clear()
        self.loop(expr, ranges)

    def process(self, charset_expr, char_range):
        r = char_range

        for target_range in self.target:
            if r.begin <= target_range.begin and target_range.end <= r.end:
                charset_expr.ranges.append(target_range)


class EpsilonNfaAlgorithm(Algorithm):
    def __init__(self):
        self.e_nfa = Automation()

    def generate_e_nfa(self, expr):
        expr_type = expr.__class__
        func_dict = {SequenceExpression:   self.seq_e_nfa,
                     AlternateExpression:  self.alt_e_nfa,
                     LoopExpression:       self.loop_e_nfa,
                     CharsetExpression:    self.charset_e_nfa}
        func = func_dict[expr_type]
        return func(expr)

    def seq_e_nfa(self, expr):
        left_nfa = self.generate_e_nfa(expr.left)
        right_nfa = self.generate_e_nfa(expr.right)
        return self.connect(left_nfa, right_nfa)

    def alt_e_nfa(self, expr):
        target = self.e_nfa
        new_e_nfa = EpsilonNfa()
        new_e_nfa.start = target.new_state()
        new_e_nfa.end = target.new_state()

        left_nfa = self.generate_e_nfa(expr.left)
        right_nfa = self.generate_e_nfa(expr.right)

        target.new_epsilon(new_e_nfa.start, left_nfa.start)
        target.new_epsilon(new_e_nfa.start, right_nfa.start)
        target.new_epsilon(left_nfa.end, new_e_nfa.end)
        target.new_epsilon(right_nfa.end, new_e_nfa.end)

        return new_e_nfa

    def loop_e_nfa(self, expr):
        target = self.e_nfa
        new_e_nfa = None
        body = self.generate_e_nfa(expr.expression)
        # 连接min个e_nfa
        for i in range(expr.min):
            copy_body = deepcopy(body)
            State.count += 1
            copy_body.start.id = State.count
            State.count += 1
            copy_body.end.id = State.count
            new_e_nfa = self.connect(new_e_nfa, copy_body)

        if expr.max == -1:
            # 连接一个循环的e_nfa
            if not new_e_nfa:
                new_e_nfa = EpsilonNfa()
                new_e_nfa.start = new_e_nfa.end = target.new_state()
            loop_start = new_e_nfa.end
            loop_end = target.new_state()
            target.new_epsilon(loop_start, body.start)
            target.new_epsilon(body.end, loop_start)
            target.new_epsilon(loop_start, loop_end)
            new_e_nfa.end = loop_end
        else:
            # 连接min到max个e_nfa
            loop_end = target.new_state()
            for i in range(expr.min, expr.max):
                copy_body = deepcopy(body)
                target.new_epsilon(copy_body.start, loop_end)
                new_e_nfa = self.connect(new_e_nfa, copy_body)
            target.new_epsilon(new_e_nfa.end, loop_end)
            new_e_nfa.end = loop_end

        return new_e_nfa

    def charset_e_nfa(self, expr):
        target = self.e_nfa
        new_e_nfa = EpsilonNfa()
        new_e_nfa.start = target.new_state()
        new_e_nfa.end = target.new_state()
        for r in expr.ranges:
            target.new_transition(new_e_nfa.start, new_e_nfa.end, r)
        return new_e_nfa

    def connect(self, nfa_a, nfa_b):
        target = self.e_nfa
        if nfa_a:
            target.new_epsilon(nfa_a.end, nfa_b.start)
            nfa_a.end = nfa_b.end
            return nfa_a
        else:
            return nfa_b


def sort_func(char_range_a, char_range_b):
    return ord(char_range_a.begin) - ord(char_range_b.begin)


def prior_char(char):
    return chr(ord(char) - 1)


def next_char(char):
    return chr(ord(char) + 1)


def generate_e_nfa(expr):
    algorithm = EpsilonNfaAlgorithm()
    temp_e_nfa = algorithm.generate_e_nfa(expr)
    e_nfa = algorithm.e_nfa
    e_nfa.start = temp_e_nfa.start
    e_nfa.finals.add(temp_e_nfa.end)
    return e_nfa


def normalize_charset(expr):
    algorithm = BuildNormalizedCharSetAlgorithm()
    algorithm.apply(expr)
    normalized_charset = algorithm.target

    algorithm = SetNormalizedCharSetAlgorithm(normalized_charset)
    algorithm.apply(expr)
    return algorithm.target
