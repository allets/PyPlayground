me = "A"
print(f"enter {me}\n"
      f"  name = `{__name__}`\n")

from . import V2B


def response_A(who):
    print(f"{me} <--- {who}\n")


V2B.request_B(me)

print(f"leave {me}\n"
      f"  name = `{__name__}`\n")
