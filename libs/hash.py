
def hash(state):
    if isinstance(state.arg, (int,float)):
        return int(state.arg)
    elif isinstance(state.arg, str):
        k = 0
        for i in state.arg:
            i = ord(i)
            k = ((i ** 2) << k) % 99_999_999
        return define(state.name, k)