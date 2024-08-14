
def call(state):
    if "hash" in state.functions:
        return state.modules.hash(state)
    else:
        hashmod = getlibs("hash.py")
        state.functions["hash"] = hashmod.hash
        return hashmod.hash(state)

def test(state):
    log(state.arg)