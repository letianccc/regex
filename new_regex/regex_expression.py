
class Expression(object):
    pass


class CharsetExpression(Expression):
    def __init__(self):
        self.ranges = list()
        self.reverse = False

    def add_range_with_conflict(self, char_range):
        b = char_range.begin
        e = char_range.end
        if char_range.begin > char_range.end:
            raise Exception("add_range")
        else:
            for r in self.ranges:
                if (r.begin <= b <= r.end) or (r.begin <= e <= r.end):
                    raise Exception("add_range")
            self.ranges.append(char_range)

    def add_range(self, char_range):
        self.ranges.append(char_range)


class SequenceExpression(Expression):
    def __init__(self):
        self.left = None
        self.right = None


class LoopExpression(Expression):
    def __init__(self):
        self.expression = None
        self.min = None
        self.max = None


class AlternateExpression(Expression):
    def __init__(self):
        self.left = None
        self.right = None

