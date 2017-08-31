from new_regex.regex_parser import Parser
from new_regex.regex_automation import nfa_to_dfa, e_nfa_to_nfa
from new_regex.interpreter import match
from new_regex.regex_algorithm import normalize_charset, generate_e_nfa


def test(re, inputs):
    print(inputs)
    print()
    parser = Parser(re)
    expr = parser.parse()

    normalize_charset(expr)
    e_nfa = generate_e_nfa(expr)
    nfa = e_nfa_to_nfa(e_nfa)
    dfa = nfa_to_dfa(nfa)

    is_match, match_chars = match(inputs, dfa)
    print("result: ", is_match)
    s = ""
    if match_chars:
        for c in match_chars:
            s += c
    else:
        print(None)
    print("match_chars: ", s)
    print()

test("\D*", "dsf1231__abc")
test("\d*", "abcde12345abcde")
test("\d+", "12abcde")

test("(/+|-)?\d+", "abcde12345abcde")
test("(\+|-)?\d+", "abcde+12345abcde")
test("(\+|-)?\d+", "abcde-12345abcde")
test("(\+|-)?\d+", "12345abcde")
test("(\+|-)?\d+", "+12345abcde")
test("(\+|-)?\d+", "-+zhl+-")   # False

test("(\+|-)?\d+(.\d+)?", "abcde12345abcde")
test("(\+|-)?\d+(.\d+)?", "abcde+12345abcde")
test("(\+|-)?\d+(.\d+)?", "abcde-12345abcde")
test("(\+|-)?\d+(.\d+)?", "abcde12345.abcde")   # F
test("(\+|-)?\d+(.\d+)?", "abcde+12345.abcde")  # F
test("(\+|-)?\d+(.\d+)?", "abcde-12345.abcde")  # F
test("(\+|-)?\d+(.\d+)?", "abcde12345.54321abcde")
test("(\+|-)?\d+(.\d+)?", "abcde+12345.54321abcde")
test("(\+|-)?\d+(.\d+)?", "abcde-12345.54321abcde")
test("(\+|-)?\d+(.\d+)?", "12345")
test("(\+|-)?\d+(.\d+)?", "+12345")
test("(\+|-)?\d+(.\d+)?", "-12345")
test("(\+|-)?\d+(.\d+)?", "12345.")     # F
test("(\+|-)?\d+(.\d+)?", "+12345.")    # F
test("(\+|-)?\d+(.\d+)?", "-12345.")    # F

test("\"([^\\\\\"]|\\\\\\.)*\"", "abc\"de\"fg")
test("/\\*([^*]|\\*+[^*/])*\\*+/", "abc/*de*/fg")
test("\"([^\\\\\"]|\\\\\\.)*\"", "abc\"d\\r\\ne\"fg")  # False



