me = "B"
print(f"enter {me}\n"
      f"  name = `{__name__}`\n")

from . import A


def circular_import_ok():
    A.request_A(me)


def request_B(who):
    print(f"{who} ---> {me}\n")
    A.response_A(me)


def response_B(who):
    print(f"{me} <--- {who}\n")


if __name__ == "__main__":
    circular_import_ok()

print(f"leave {me}\n"
      f"  name = `{__name__}`\n")
