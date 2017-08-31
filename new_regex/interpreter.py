# 匹配失败后，如果已经到达最终状态，返回匹配结果，否则继续匹配
def match(inputs, dfa):
    length = len(inputs)
    index = 0

    match_chars = list()
    is_final = False
    is_range_match = False
    cur_state = dfa.start
    while index < length:
        c = inputs[index]
        for t in cur_state.transitions:
            r = t.char_range
            if r.begin <= c <= r.end:
                is_range_match = True
                match_chars.append(c)

                if t.target in dfa.finals:
                    is_final = True
                else:
                    is_final = False
                cur_state = t.target
                break
            else:
                is_range_match = False

        if not is_range_match:
            if is_final:
                return is_final, match_chars
            else:
                match_chars.clear()
        index += 1

    return is_final, match_chars

