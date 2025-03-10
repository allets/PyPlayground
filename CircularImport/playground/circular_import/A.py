me = "A"
print(f"enter {me}\n"
      f"  name = `{__name__}`\n")

from .B import request_B, response_B


def circular_import_error():
    request_B(me)


def request_A(who):
    print(f"{who} ---> {me}\n")
    response_B(me)


def response_A(who):
    print(f"{me} <--- {who}\n")


if __name__ == "__main__":
    circular_import_error()

print(f"leave {me}\n"
      f"  name = `{__name__}`\n")
