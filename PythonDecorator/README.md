# Python Decorator

```
# 無參數的裝飾器
python -m playground.python_decorator.dec_0_param

# 有參數的裝飾器
python -m playground.python_decorator.dec_n_params
```



## 無參數的裝飾器

目標是達成 `fn = dec1(f)`



裝飾器 x 1
```py
def dec1(func):
	print("1")
	return func


# dec1 也能是下列，但效果不太一樣
def dec_w1(func):
	def wrapper(msg):
		print("1")
		return func(msg)
	return wrapper


def f(msg):
    print(msg)


@dec1
def f1(msg):
    print(msg)


@dec_w1
def f2(msg):
    print(msg)


# f1 = dec1(f)
f1("ok")
# 這時不會出現「1」，而是在定義 f1 時就 print 了
# ok

f2("ok")
# 1
# ok
```


裝飾器 x N
```py
# N = 3

@dec3
@dec2
@dec1
def f1(msg):
    print(msg)


# f1 = dec3(dec2(dec1(f)))
f1("ok") # 上述 **無** wrapper 的結果:
# 這時不會出現「1」、「2」、「3」，而是在定義 f1 時就 print 了
# ok

f2("ok") # 上述 **有** wrapper 的結果:
# 3
# 2
# 1
# ok
```



## 有參數的裝飾器

目標是達成 `fn = dec1("a1")(f)`

有參數的裝飾器 相當於
回傳一個裝飾器。



裝飾器 x 1
```py
def dec1(a1):
	def new_dec(func):
		print("1")
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


def f(msg):
    print(msg)


@dec1("a1")
def f1(msg):
    print(msg)


@dec_w1("a1")
def f2(msg):
    print(msg)


# f1 = dec1("a1")(f)
f1("ok")
# 這時不會出現「1」，而是在定義 f1 時就 print 了
# ok

f2("ok")
# 1
# ok
```


裝飾器 x N
```py
# N = 3

@dec3("a3")
@dec2("a2")
@dec1("a1")
def f1(msg):
    print(msg)


# f1 = dec3("a3")(dec2("a2")(dec1("a1")(f)))
f1("ok") # 上述 **無** wrapper 的結果:
# 這時不會出現「1」、「2」、「3」，而是在定義 f1 時就 print 了
# ok

f2("ok") # 上述 **有** wrapper 的結果:
# 3
# 2
# 1
# ok
```



## 教材

PEP 318 – Decorators for Functions and Methods  
https://peps.python.org/pep-0318/#current-syntax  
(Author: Kevin D. Smith <Kevin.Smith at theMorgue.org>, Jim J. Jewett, Skip Montanaro, Anthony Baxter 
| License: Public Domain)  
```
The current syntax for function decorators as implemented in Python 2.4a2 is:

	@dec2
	@dec1
	def func(arg1, arg2, ...):
		pass

This is equivalent to:

	def func(arg1, arg2, ...):
		pass
	func = dec2(dec1(func))



The current syntax also allows decorator declarations to call a function that returns a decorator:

	@decomaker(argA, argB, ...)
	def func(arg1, arg2, ...):
		pass

This is equivalent to:

	func = decomaker(argA, argB, ...)(func)

```


