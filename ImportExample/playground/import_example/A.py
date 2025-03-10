import sys

print(
    f"enter A, "
    f"\n  __name__ = `{__name__}`"
    f"\n  __package__ = `{__package__}`"
    f"\n  sys.path[0] = `{sys.path[0]}`\n"
)

import B  # Absolute Import-1
# from playground.import_example import B  # Absolute Import-2
# from . import B  # Relative Import-1
# from ...playground.import_example import B  # Relative Import-2


def greet_each_other():
    me = "A"
    print(f"{me}: Hello!\n")
    B.greet(me)


if __name__ == "__main__":
    greet_each_other()
