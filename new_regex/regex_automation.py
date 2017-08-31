from new_regex.regex_data import CharRange


class Automation(object):
    def __init__(self):
        State.count = 0
        self.states = set()
        self.start = None
        self.finals = set()
        self.transitions = list()

    def add_final_state(self, state):
        self.finals.add(state)

    def set_start_state(self, state):
        self.start = state

    def new_state(self):
        state = State()
        self.states.add(state)
        return state

    def new_transition(self, start, end, char_range):
        t = Transition(start, end, char_range)
        start.transitions.append(t)
        self.transitions.append(t)
        return t

    def new_epsilon(self, start, end):
        t = Transition(start, end, CharRange.epsilon)
        start.transitions.append(t)
        self.transitions.append(t)


class State(object):
    def __init__(self):
        self.transitions = list()


class Transition(object):
    def __init__(self, source, target, char_range):
        self.source = source
        self.target = target
        self.char_range = char_range


class EpsilonNfa(object):
    def __init__(self):
        self.start = None
        self.end = None


def e_nfa_to_nfa(e_nfa):
    nfa = Automation()
    trans = list()
    e_nfa_states = set()
    e_nfa_state_dict = dict()   # e_nfa状态到nfa状态的映射

    s = nfa.new_state()
    e_nfa_state_dict[e_nfa.start] = s
    nfa.start = s

    state_stack = [s]
    while state_stack:
        trans.clear()
        e_nfa_states.clear()
        # 收集nfa状态对应的闭包以及与其他nfa状态的转换
        source = state_stack.pop()
        for e_nfa_state, nfa_state in e_nfa_state_dict.items():
            if source == nfa_state:
                s = e_nfa_state
                break
        collect(s, trans, e_nfa_states)
        # 建立e_nfa状态与nfa状态的映射，以及对应nfa状态与其他nfa状态的连接
        for t in trans:
            if t.target not in e_nfa_state_dict.keys():
                s = nfa.new_state()
                e_nfa_state_dict[t.target] = s

                state_stack.append(s)
            target = e_nfa_state_dict[t.target]
            nfa.new_transition(source, target, t.char_range)

        for s in e_nfa_states:
            if s in e_nfa.finals:
                nfa.finals.add(source)
    return nfa


def collect(state, transitions, e_nfa_states):
    if state not in e_nfa_states:
        e_nfa_states.add(state)
        for t in state.transitions:
            if t.char_range == CharRange.epsilon:
                collect(t.target, transitions, e_nfa_states)
            else:
                transitions.append(t)


def nfa_to_dfa(nfa):
    dfa = Automation()
    dfa_states_dict = dict()    # DFA状态对应的NFA集合
    range_dict = dict()         # 字符范围对应的NFA集合

    s = dfa.new_state()
    dfa.start = s
    dfa_states_dict[s] = {nfa.start}

    state_stack = [s]
    while state_stack:
        range_dict.clear()

        source = state_stack.pop()
        states = dfa_states_dict[source]
        # 遍历DFA状态对应的NFA状态集，得到字符范围类和对应的NFA状态集
        for s in states:
            for t in s.transitions:
                is_exist = False
                for r in range_dict.keys():
                    if t.char_range.begin == r.begin and t.char_range.end == r.end:
                        is_exist = True
                        range_dict[r].add(t.target)
                        break
                if not is_exist:
                    range_dict[t.char_range] = {t.target}
        # 遍历字符范围类，产生对应的DFA状态
        for range_class, target_nfa_states in range_dict.items():
            # 判断目标NFA状态集是否有对应的DFA状态
            target = None
            for dfa_state, nfa_states in dfa_states_dict.items():
                if nfa_states == target_nfa_states:
                    target = dfa_state
                    break

            if not target:
                target = dfa.new_state()
                dfa_states_dict[target] = target_nfa_states

                state_stack.append(target)

            dfa.new_transition(source, target, range_class)
        # 设置DFA最终状态集
        for dfa_state, nfa_states in dfa_states_dict.items():
            for s in nfa_states:
                if s in nfa.finals:
                    dfa.finals.add(dfa_state)
                    break

    return dfa

