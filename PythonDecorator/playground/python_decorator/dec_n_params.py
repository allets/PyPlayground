"""
python -m playground.python_decorator.dec_n_params
"""


def dec1(a1):
    def new_dec(func):
        print("1")
        return func

    return new_dec


def dec2(a2):
    def new_dec(func):
        print("2")
        return func

    return new_dec


def dec3(a3):
    def new_dec(func):
        print("3")
        return func

    return new_dec


# dec1 也能是下列，但效果不太一樣
def dec_w1(a1):
    def new_dec(func):
        def wrapper(msg):
            print("1")
            return func(msg)

        return wrapper

    return new_dec


def dec_w2(a2):
    def new_dec(func):
        def wrapper(msg):
            print("2")
            return func(msg)

        return wrapper

    return new_dec


def dec_w3(a3):
    def new_dec(func):
        def wrapper(msg):
            print("3")
            return func(msg)

        return wrapper

    return new_dec


def f(msg):
    print(msg)


@dec3("a3")
@dec2("a2")
@dec1("a1")
def f1(msg):
    print(msg)


@dec_w3("a3")
@dec_w2("a2")
@dec_w1("a1")
def f2(msg):
    print(msg)


def print_cmd(cmd):
    prompt = ">>> "
    print(f"{prompt}{cmd}")


print("\n--- without wrapper")
print_cmd('f0 = dec3("a3")(dec2("a2")(dec1("a1")(f)))')
f0 = dec3("a3")(dec2("a2")(dec1("a1")(f)))
# 1
# 2
# 3
print_cmd('f0("ok")')
f0("ok")
# ok

print_cmd('f1("ok")')
f1("ok")
# ok

print("\n--- with wrapper")
print_cmd('f0 = dec_w3("a3")(dec_w2("a2")(dec_w1("a1")(f)))')
f0 = dec_w3("a3")(dec_w2("a2")(dec_w1("a1")(f)))
print_cmd('f0("ok")')
f0("ok")
# 3
# 2
# 1
# ok

print_cmd('f2("ok")')
f2("ok")
# 3
# 2
# 1
# ok
