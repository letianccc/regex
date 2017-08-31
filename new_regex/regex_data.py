
class CharRange(object):
    epsilon = u"\u03B5"

    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

    def __str__(self):
        if self.begin == self.end:
            return "range " + self.begin + "(" + str(ord(self.begin)) + ")"
        else:
            return "range " + self.begin + "(" + str(ord(self.begin)) + ")" + " " + self.end + "(" + str(ord(self.end)) + ")"




