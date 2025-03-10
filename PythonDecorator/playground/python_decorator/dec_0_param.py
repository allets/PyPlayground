"""
python -m playground.python_decorator.dec_0_param
"""


def dec1(func):
    print("1")
    return func


def dec2(func):
    print("2")
    return func


def dec3(func):
    print("3")
    return func


# dec1 也能是下列，但效果不太一樣
def dec_w1(func):
    def wrapper(msg):
        print("1")
        return func(msg)

    return wrapper


def dec_w2(func):
    def wrapper(msg):
        print("2")
        return func(msg)

    return wrapper


def dec_w3(func):
    def wrapper(msg):
        print("3")
        return func(msg)

    return wrapper


def f(msg):
    print(msg)


@dec3
@dec2
@dec1
def f1(msg):
    print(msg)


@dec_w3
@dec_w2
@dec_w1
def f2(msg):
    print(msg)


def print_cmd(cmd):
    prompt = ">>> "
    print(f"{prompt}{cmd}")


print("\n--- without wrapper")
print_cmd("f0 = dec3(dec2(dec1(f)))")
f0 = dec3(dec2(dec1(f)))
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
print_cmd("f0 = dec_w3(dec_w2(dec_w1(f)))")
f0 = dec_w3(dec_w2(dec_w1(f)))
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
