me = "B"
print(f"enter {me}\n"
      f"  name = `{__name__}`\n")

from . import V2A


def request_B(who):
    print(f"{who} ---> {me}\n")
    V2A.response_A(me)


print(f"leave {me}\n"
      f"  name = `{__name__}`\n")
