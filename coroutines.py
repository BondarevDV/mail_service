from inspect import getgeneratorlocals

def subgen():
    x = 'ready to ascept message'
    message = yield x
    print("subgen receive: ", message)