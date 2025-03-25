# Python Import

解決多入口點的 import 問題，分析過程、說明錯誤。


**只論 Python 3.8 的執行結果。**


Project structure:
```
- ImportExample/
	- main.py
	- playground/import_example/
		- __init__.py
		- A.py
		- B.py
```



## Use Case

main import A，
A import B。

main 總是作為入口點，
A 偶爾被獨立使用作為入口點。



### Q&A: A 要如何 import B 才能達成被 import 和 獨立作為入口點？

1)  下指令執行 main（A 被 import）及 下指令執行 A（A 獨立作為入口點），
	兩者 搜尋 B 模組的基準點 必須相同，
	即兩者的 `sys.path[0]` 必須相同。

	例：
	在使用指令 `python main.py` 或 `python -m main` 的前提下，
	其 `sys.path[0]` 皆為 `C:\IdeaProject\PyPlayground\ImportExample`。
	
	所以 A 無論使用 Absolute 或 Relative import B，
	執行 A 的指令其 `sys.path[0]` 也必須為 `C:\IdeaProject\PyPlayground\ImportExample`，
	因此使用指令 `python -m playground.import_example.A`。
	
	不使用指令 `python ./playground/import_example/A.py`，
	因為其 `sys.path[0]` 為 `C:\IdeaProject\PyPlayground\ImportExample\playground\import_example`，
	不同於上列！


2)  雖然 A 無論使用 Absolute 或 Relative import B 都可以，
	建議使用「Absolute - 2」或「Relative - 1」的方式。



## Analysis

### `sys.path[0]`

[`sys.path` – Python 3 Library Reference](https://docs.python.org/3.12/library/sys.html#sys.path)：
> A list of strings that specifies the search path for modules. 
> 
> - `python -m module` command line: prepend the current working directory.
> - `python script.py` command line: prepend the script’s directory. If it’s a symbolic link, resolve symbolic links.

Python 在 `sys.path` 裡面搜尋模組。

本文範例的目錄結構簡單，且沒有對 `sys.path` 加工操作，故只論 `sys.path[0]`。

所以得出下列 `sys.path[0]`：

|   | command                                 | sys.path[0]                                                         |
|---|-----------------------------------------|---------------------------------------------------------------------|
| 1 | python main.py                          | C:\IdeaProject\PyPlayground\ImportExample                           |
| 2 | python -m main                          | C:\IdeaProject\PyPlayground\ImportExample                           |
| 3 | python ./playground/import_example/A.py | C:\IdeaProject\PyPlayground\ImportExample\playground\import_example |
| 4 | python -m playground.import_example.A   | C:\IdeaProject\PyPlayground\ImportExample                           |



### Import 方式

| Import       | in `A.py`                                  |
|--------------|--------------------------------------------|
| Absolute - 1 | import B                                   |
| Absolute - 2 | from playground.import_example import B    |
| Relative - 1 | from . import B                            |
| Relative - 2 | from ...playground.import_example import B |


[What’s New in Python 3.0](https://docs.python.org/3.0/whatsnew/3.0.html#removed-syntax)：
> The only acceptable syntax for relative imports is `from .[module] import name`. 
> All import forms not starting with `.` are interpreted as absolute imports. (PEP 0328)

因為 Python 3 不支援 implicit relative import（路徑開頭不加 `.` 的寫法），
故將「Absolute - 1」的寫法視為 absolute import。



### 執行結果

[Python 3 Tutorial](https://docs.python.org/3.12/tutorial/modules.html#intra-package-references):
> Note that relative imports are based on the name of the current module. 
> Since the name of the main module is always `"__main__"`, 
> modules intended for use as the main module of a Python application must always use absolute imports.


[PEP 328 – Imports: Multi-Line and Absolute/Relative](https://peps.python.org/pep-0328/#relative-imports-and-name)  
(Author: Aahz <aahz@pythoncraft.com> 
| License: Public Domain):
> Relative imports use a module’s `__name__` attribute to determine that module’s position in the package hierarchy. 
> If the module’s name does not contain any package information (e.g. it is set to ‘`__main__`’) 
> then relative imports are resolved as if the module were a top level module, 
> regardless of where the module is actually located on the file system.


[PEP 366 – Main module explicit relative imports](https://peps.python.org/pep-0366)  
(Author: Alyssa Coghlan <ncoghlan@gmail.com> 
| License: Public Domain):
> ## Abstract
> 
> This PEP proposes a backwards compatible mechanism that permits the use of 
> explicit relative imports from executable modules within packages.
> Such imports currently fail due to an awkward interaction between PEP 328 and PEP 338.

依本文探討的案例當 A 獨立作為入口點，
在 A （`__main__` 模組）使用 relative import，
以前的結果會異常；
經過 PEP 366 的努力，結果好轉了……
 
> By adding a new module level attribute, this PEP 
> allows relative imports to work automatically if the module is executed using the `-m` switch.

上面這句說：`python -m pkg.xxx` 在 xxx 使用 relative import 完全沒問題。

> A small amount of boilerplate in the module itself will 
> allow the relative imports to work when the file is executed by name.

上面這句說：`python ./pkg/yyy.py` 在 yyy 使用 relative import 的話，需要額外寫幾行程式碼才能正常運作。

> 
> ## Proposed Change
> 
> The major proposed change is the introduction of a new module level attribute, `__package__`. 
> When it is present, relative imports will be based on this attribute rather than the module `__name__` attribute.
> 
> ...  
> 
> The `runpy` module will explicitly set the new attribute, 
> basing it off the name used to locate the module to be executed 
> rather than the name used to set the module’s `__name__` attribute. 
> This will allow relative imports to work correctly from main modules executed with the `-m` switch.
> 

下面這段說明 `python ./pkg/yyy.py` 在 yyy 使用 relative import 的話，
需要在 import 之前手動設定 `__package__ = "pkg"`（如下），
且須確保 import 機制從 `sys.path` 中找得到 pkg 目錄，
一切才能正常運作。

> When the main module is specified by its filename, 
> then the `__package__` attribute will be set to `None`. 
> To allow relative imports when the module is executed directly, 
> boilerplate similar to the following would be needed before the first relative import statement:
> 
>     if __name__ == "__main__" and __package__ is None:
>         __package__ = "expected.package.name"
> 
> Note that this boilerplate is sufficient only if the top level package is already accessible via `sys.path`. 
> Additional code that manipulates `sys.path` would be needed 
> in order for direct execution to work without the top level package already being importable.
>
> Note that setting `__package__` to the empty string explicitly is permitted, 
> and has the effect of disabling all relative imports from that module 
> (since the import machinery will consider it to be a top level module in that case). 
> This means that tools like `runpy` do not need to provide special case 
> handling for top level modules when setting `__package__`.

綜合上列說明下列執行結果：

| Importx指令  | Exception                                                           |
|--------------|---------------------------------------------------------------------|
| Absolute - 1 | ===                                                                 |
| 1            | ModuleNotFoundError: B                                              |
| 2            | ModuleNotFoundError: B                                              |
| 3            |                                                                     |
| 4            | ModuleNotFoundError: B                                              |
|              |                                                                     |
| Absolute - 2 | ===                                                                 |
| 1            |                                                                     |
| 2            |                                                                     |
| 3            | ModuleNotFoundError: playground                                     |
| 4            |                                                                     |
|              |                                                                     |
| Relative - 1 | ===                                                                 |
| 1            |                                                                     |
| 2            |                                                                     |
| 3            | ImportError: attempted relative import with no known parent package |
| 4            |                                                                     |
|              |                                                                     |
| Relative - 2 | ===                                                                 |
| 1            | ValueError: attempted relative import beyond top-level package      |
| 2            | ValueError: attempted relative import beyond top-level package      |
| 3            | ImportError: attempted relative import with no known parent package |
| 4            | ValueError: attempted relative import beyond top-level package      |



| Importx指令  | 結果說明                                                                                       |
|--------------|--------------------------------------------------------------------------------------------|
| Absolute - 1 | ===                                                                                        |
| 1            | `sys.path[0]`(ImportExample) 底下沒有 B                                                        |
| 2            | 同本節項目 1                                                                                    |
| 3            | `sys.path[0]`(import_example) 底下有 B                                                        |
| 4            | 同本節項目 1                                                                                    |
|              |                                                                                            |
| Absolute - 2 | ===                                                                                        |
| 1            | `sys.path[0]`(ImportExample) 底下有 playground                                                |
| 2            | 同本節項目 1                                                                                    |
| 3            | `sys.path[0]`(import_example) 底下沒有 playground                                              |
| 4            | 同本節項目 1                                                                                    |
|              |                                                                                            |
| Relative - 1 | ===                                                                                        |
| 1            | `A.__package__` 為 `playground.import_example`，能用於計算 relative import 路徑                     |
| 2            | 同本節項目 1                                                                                    |
| 3            | `A.__package__` 為 `None`，即沒有 parent package 能用於計算 relative import 路徑                       |
| 4            | 同本節項目 1                                                                                    |
|              |                                                                                            |
| Relative - 2 | ===                                                                                        |
| 1            | `A.__package__` 為 `playground.import_example` 但 import 不能超過 top-level package (playground) |
| 2            | 同本節項目 1                                                                                    |
| 3            | 同上節項目 3                                                                                    |
| 4            | 同本節項目 1                                                                                    |


以「Import方式x指令」呈現 A import B 的執行結果：
-   同一 Import 方式時，清楚地顯示雖然指令不同但在對應的 `sys.path[0]` 相同（搜尋 B 模組的基準點相同）的情況下，執行結果是一樣的，
    如指令 1、2、4。
-   相同 Import 方式搭配不同 `sys.path[0]` 會有不同執行結果，如指令 3 對比 1/2/4。
-   同一個 `sys.path[0]` 的情況下，使用哪一種 Import 方式比較適合。
    -   指令 1/2/4：「Absolute - 2」或「Relative - 1」。
    -   指令 3：「Absolute - 1」。


[What’s New In Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html#deprecated)
> Setting `__package__` or `__cached__` on a module is deprecated, 
> and will cease to be set or taken into consideration by the import system in Python 3.14. 
> (Contributed by Brett Cannon in [gh-65961](https://github.com/python/cpython/issues/65961).)

[`__package__` – Python 3 Language Reference](https://docs.python.org/3.12/reference/datamodel.html#module.__package__)
> It is **strongly** recommended that you use `module.__spec__.parent` instead of `module.__package__`.
> `__package__` is now only used as a fallback if `__spec__.parent` is not set, and this fallback path is deprecated.
> 
> Changed in version 3.6: The value of `__package__` is expected to be the same as `__spec__.parent`.

注意！最好請以 `__spec__.parent ` 取代 `__package__`。



### Absolute Import-1 Log

`@A.py`
```
import B
```


`python main.py`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

Traceback (most recent call last):
  File "main.py", line 1, in <module>
    from playground.import_example import A
  File "C:\IdeaProject\PyPlayground\ImportExample\playground\import_example\A.py", line 10, in <module>
    import B  # Absolute Import-1
ModuleNotFoundError: No module named 'B'
```


`python -m main`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

Traceback (most recent call last):
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "C:\IdeaProject\PyPlayground\ImportExample\main.py", line 1, in <module>
    from playground.import_example import A
  File "C:\IdeaProject\PyPlayground\ImportExample\playground\import_example\A.py", line 10, in <module>
    import B  # Absolute Import-1
ModuleNotFoundError: No module named 'B'
```


`python ./playground/import_example/A.py`
```
enter A,
  __name__ = `__main__`
  __package__ = `None`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample\playground\import_example`

A: Hello!

B: Hello, A!

```


`python -m playground.import_example.A`
```
enter A,
  __name__ = `__main__`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

Traceback (most recent call last):
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "C:\IdeaProject\PyPlayground\ImportExample\playground\import_example\A.py", line 10, in <module>
    import B  # Absolute Import-1
ModuleNotFoundError: No module named 'B'
```



### Absolute Import-2 Log


`@A.py`
```
from playground.import_example import B
```


`python main.py`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

A: Hello!

B: Hello, A!

```


`python -m main`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

A: Hello!

B: Hello, A!

```


`python ./playground/import_example/A.py`
```
enter A,
  __name__ = `__main__`
  __package__ = `None`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample\playground\import_example`

Traceback (most recent call last):
  File "./playground/import_example/A.py", line 11, in <module>
    from playground.import_example import B  # Absolute Import-2
ModuleNotFoundError: No module named 'playground'
```


`python -m playground.import_example.A`
```
enter A,
  __name__ = `__main__`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

A: Hello!

B: Hello, A!

```



### Relative Import-1 Log


`@A.py`
```
from . import B
```


`python main.py`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

A: Hello!

B: Hello, A!

```


`python -m main`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

A: Hello!

B: Hello, A!

```


`python ./playground/import_example/A.py`
```
enter A,
  __name__ = `__main__`
  __package__ = `None`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample\playground\import_example`

Traceback (most recent call last):
  File "./playground/import_example/A.py", line 12, in <module>
    from . import B  # Relative Import-1
ImportError: attempted relative import with no known parent package
```


`python -m playground.import_example.A`
```
enter A,
  __name__ = `__main__`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

A: Hello!

B: Hello, A!

```



### Relative Import-2 Log


`@A.py`
```
from ...playground.import_example import B
```


`python main.py`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

Traceback (most recent call last):
  File "main.py", line 1, in <module>
    from playground.import_example import A
  File "C:\IdeaProject\PyPlayground\ImportExample\playground\import_example\A.py", line 13, in <module>
    from ...playground.import_example import B  # Relative Import-2
ValueError: attempted relative import beyond top-level package
```


`python -m main`
```
enter A,
  __name__ = `playground.import_example.A`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

Traceback (most recent call last):
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "C:\IdeaProject\PyPlayground\ImportExample\main.py", line 1, in <module>
    from playground.import_example import A
  File "C:\IdeaProject\PyPlayground\ImportExample\playground\import_example\A.py", line 13, in <module>
    from ...playground.import_example import B  # Relative Import-2
ValueError: attempted relative import beyond top-level package
```


`python ./playground/import_example/A.py`
```
enter A,
  __name__ = `__main__`
  __package__ = `None`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample\playground\import_example`

Traceback (most recent call last):
  File "./playground/import_example/A.py", line 13, in <module>
    from ...playground.import_example import B  # Relative Import-2
ImportError: attempted relative import with no known parent package
```


`python -m playground.import_example.A`
```
enter A,
  __name__ = `__main__`
  __package__ = `playground.import_example`
  sys.path[0] = `C:\IdeaProject\PyPlayground\ImportExample`

Traceback (most recent call last):
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "C:\IdeaProject\PyPlayground\ImportExample\playground\import_example\A.py", line 13, in <module>
    from ...playground.import_example import B  # Relative Import-2
ValueError: attempted relative import beyond top-level package
```


