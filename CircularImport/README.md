# Circular Import

為了了解 Circular Import Error，看過官方文件、前輩文章，最後跑去追蹤 CPython 原始碼。

1.  `ImportError: cannot import name 'xxx' from partially initialized module 'XX' (most likely due to a circular import) (/path/to/XX.py)`
2.  `AttributeError: partially initialized module 'XX' has no attribute 'xxx' (most likely due to a circular import)`



## Sample Code

除了本倉庫範例程式，
[CPython CircularImportTests](https://github.com/python/cpython/blob/a030bae5/Lib/test/test_import/__init__.py#L1592)
呈現各種不同樣態的 Circular Import 範例。


```
# (1) ImportError
python -m playground.circular_import.A

# import ok
python -m playground.circular_import.B

# (2) AttributeError
python -m playground.circular_import.V2A

# import ok
python -m playground.circular_import.V2B
```



`python -m playground.circular_import.A`
```
enter A
  name = `__main__`

enter B
  name = `playground.circular_import.B`

enter A
  name = `playground.circular_import.A`

Traceback (most recent call last):
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "C:\IdeaProject\PyPlayground\CircularImport\playground\circular_import\A.py", line 5, in <module>
    from .B import request_B, response_B
  File "C:\IdeaProject\PyPlayground\CircularImport\playground\circular_import\B.py", line 5, in <module>
    from . import A
  File "C:\IdeaProject\PyPlayground\CircularImport\playground\circular_import\A.py", line 5, in <module>
    from .B import request_B, response_B
ImportError: cannot import name 'request_B' from partially initialized module 'playground.circular_import.B' (most likely due to a circular import) (C:\IdeaProject\PyPlayground\CircularImport\playground\circular_import\B.py)
```


`python -m playground.circular_import.B`
```
enter B
  name = `__main__`

enter A
  name = `playground.circular_import.A`

enter B
  name = `playground.circular_import.B`

leave B
  name = `playground.circular_import.B`

leave A
  name = `playground.circular_import.A`

B ---> A

B <--- A

leave B
  name = `__main__`

```


`python -m playground.circular_import.V2A`
```
enter A
  name = `__main__`

enter B
  name = `playground.circular_import.V2B`

enter A
  name = `playground.circular_import.V2A`

Traceback (most recent call last):
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "C:\IdeaProject\PyPlayground\CircularImport\playground\circular_import\V2A.py", line 5, in <module>
    from . import V2B
  File "C:\IdeaProject\PyPlayground\CircularImport\playground\circular_import\V2B.py", line 5, in <module>
    from . import V2A
  File "C:\IdeaProject\PyPlayground\CircularImport\playground\circular_import\V2A.py", line 12, in <module>
    V2B.request_B(me)
AttributeError: partially initialized module 'playground.circular_import.V2B' has no attribute 'request_B' (most likely due to a circular import)
```


`python -m playground.circular_import.V2B`
```
enter B
  name = `__main__`

enter A
  name = `playground.circular_import.V2A`

enter B
  name = `playground.circular_import.V2B`

leave B
  name = `playground.circular_import.V2B`

A ---> B

A <--- B

leave A
  name = `playground.circular_import.V2A`

leave B
  name = `__main__`

```



## Circular Import 的說明與解法

推薦下列文章：
-   2001-02-02 Importing Python Modules | Effbot (Fredrik Lundh)  
    https://web.archive.org/web/20200917011425/https://effbot.org/zone/import-confusion.htm#circular-imports  
    
    "Circular Imports" 這段說明簡短清楚，超級推薦！
    
    原本想要備份那整段在這，
    但是[他不授權文章內容轉貼](https://web.archive.org/web/20200907054207/https://effbot.org/zone/copyright.htm)，
    且他去找上帝喝咖啡了，
    為了尊重版權，
    只能私藏了。

-   2024-05-07 Python import: Advanced Techniques and Tips | Geir Arne Hjelle @ Real Python  
    https://realpython.com/python-import/#handle-cyclical-imports  

    "Handle Cyclical Imports" 段落中，陰陽範例程式演化了執行正常、異常到解法，有細緻度卻好懂。

-   2017-10-30 Python 的 Import 陷阱 | pyliaorachel (Rachel Liao) @ PyLadies Taiwan  
    https://medium.com/pyladies-taiwan/3538e74f57e3#fadc  

    "Trap 1: Circular Import" 段落中，除了範例程式，還有條列出重點。



## partially initialized module

上列 2 種 Error 都提到「partially initialized module」，
這究竟是什麼？

模組（Module）需要被 import 之後才能使用，因此從 import 的運作開始了解……  

import 的過程發生什麼事？  
[Python 3 Language Reference > The import system](https://docs.python.org/3.12/reference/import.html#the-import-system)
> Functions such as `importlib.import_module()` and built-in `__import__()` 
> can also be used to invoke the import machinery.

因為看完該篇文件後，沒找到「partially initialized module」的解釋，所以決定追原始碼。

在追 `importlib.import_module(name, package=None)` 的過程中，  
很快地發現了 `spec._initializing`：  
-   在 module 放入 cache 之前，被賦值 `True`。
-   在 loader 執行 module 並將其更新到 cache 之後，被賦值 `False`。

https://github.com/python/cpython/blob/a030bae5/Lib/importlib/_bootstrap.py#L923-L950
```py
def _load_unlocked(spec):
    # ...

    # This must be done before putting the module in sys.modules
    # (otherwise an optimization shortcut in import.c becomes
    # wrong).
    spec._initializing = True
    try:
        sys.modules[spec.name] = module
        try:
            if spec.loader is None:
                if spec.submodule_search_locations is None:
                    raise ImportError('missing loader', name=spec.name)
                # A namespace package so do nothing.
            else:
                spec.loader.exec_module(module)
        except:
            try:
                del sys.modules[spec.name]
            except KeyError:
                pass
            raise
        # Move the module to the end of sys.modules.
        # We don't ensure that the import-related module attributes get
        # set in the sys.modules replacement case.  Such modules are on
        # their own.
        module = sys.modules.pop(spec.name)
        sys.modules[spec.name] = module
        _verbose_message('import {!r} # {!r}', spec.name, spec.loader)
    finally:
        spec._initializing = False

    return module
```


ModuleSpec [官方文件](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.ModuleSpec)
沒有列出屬性 `_initializing` 的說明。

沒找到官方文件說明，好吧……我只能推測了……  
`ModuleSpec._initializing` 用來告訴 import 運作的涉案者這個模組物件正在初始化當中，
使用它之前可能要先檢查一下這個指示燈，再決定要怎麼跟它互動。



### Error 從哪生出來？

因為沒找到 `ModuleSpec._initializing` 的官方說明，
要更進一步求證它就是我認為的那個 **partially initialized** module，
在沒有更多線索的情況下，
只好追蹤是原始碼的哪一行發出上列 2 種 Error。



#### 1. ImportError

在錯誤訊息的字串格式中，
呼叫了 `_PyModuleSpec_IsInitializing(spec)` 來變化訊息，
進一步追蹤該 function 後，確認等同於 `ModuleSpec._initializing`。
到此算是驗證完成。


https://github.com/python/cpython/blob/a030bae5/Python/ceval.c#L2555-L2565
```c
static PyObject *
import_from(PyThreadState *tstate, PyObject *v, PyObject *name)
{
    // ...
    
 error:
    // ...
    
        PyObject *spec = PyObject_GetAttr(v, &_Py_ID(__spec__));
        const char *fmt =
            _PyModuleSpec_IsInitializing(spec) ?
            "cannot import name %R from partially initialized module %R "
            "(most likely due to a circular import) (%S)" :
            "cannot import name %R from %R (%S)";
        Py_XDECREF(spec);

        errmsg = PyUnicode_FromFormat(fmt, name, pkgname_or_unknown, pkgpath);
        /* NULL checks for errmsg and pkgname done by PyErr_SetImportError. */
        _PyErr_SetImportErrorWithNameFrom(errmsg, pkgname, pkgpath, name);
 
    // ...   
}
```


https://github.com/python/cpython/blob/a030bae5/Objects/moduleobject.c#L743
```c
/* Check if the "_initializing" attribute of the module spec is set to true.
   Clear the exception and return 0 if spec is NULL.
 */
int
_PyModuleSpec_IsInitializing(PyObject *spec)
{
    if (spec != NULL) {
        PyObject *value;
        int ok = _PyObject_LookupAttr(spec, &_Py_ID(_initializing), &value);
        if (ok == 0) {
            return 0;
        }
        if (value != NULL) {
            int initializing = PyObject_IsTrue(value);
            Py_DECREF(value);
            if (initializing >= 0) {
                return initializing;
            }
        }
    }
    PyErr_Clear();
    return 0;
}
```



###### 既然都找到 function `import_from` 了，來看看究竟是哪一行發生 `goto error;`

function `import_from` 流程大約為：
若 mod.attr （名為 name 的屬性）存在，則返回其結果；
若不存在，則尋找同名的 mod.submod （名為 name 的附屬模組）。
完整原始碼請見後續。

單看原始碼可推測：
-   function `import_from` 參數 v 為模組物件、name 為字串

以錯誤訊息比對原始碼能確定： 
-   name 為 request_B
-   pkgname 為 playground.circular_import.B

上述能證明下列推導：
-   程式至少執行到 `x = PyImport_GetModule(fullmodname);` 這行

所以 fullmodname 為 playground.circular_import.B.request_B，
然而 request_B 是個 function，
`x = PyImport_GetModule(fullmodname);` 一定找不到這個模組，
即 x 為 NULL，
因為這裡是最後一個 `goto error;` 了，
那麼就是這裡發生 `goto error;` 了。


想知道為什麼 x 為 NULL 卻沒噴 Error，請跳到原始碼後面的解釋。


https://github.com/python/cpython/blob/a030bae5/Python/ceval.c#L2501
```c
static PyObject *
import_from(PyThreadState *tstate, PyObject *v, PyObject *name)
{
    PyObject *x;
    PyObject *fullmodname, *pkgname, *pkgpath, *pkgname_or_unknown, *errmsg;

    if (_PyObject_LookupAttr(v, name, &x) != 0) {
        return x;
    }
    /* Issue #17636: in case this failed because of a circular relative
       import, try to fallback on reading the module directly from
       sys.modules. */
    pkgname = PyObject_GetAttr(v, &_Py_ID(__name__));
    if (pkgname == NULL) {
        goto error;
    }
    if (!PyUnicode_Check(pkgname)) {
        Py_CLEAR(pkgname);
        goto error;
    }
    fullmodname = PyUnicode_FromFormat("%U.%U", pkgname, name);
    if (fullmodname == NULL) {
        Py_DECREF(pkgname);
        return NULL;
    }
    x = PyImport_GetModule(fullmodname);
    Py_DECREF(fullmodname);
    if (x == NULL && !_PyErr_Occurred(tstate)) {
        goto error;
    }
    Py_DECREF(pkgname);
    return x;
 error:
    pkgpath = PyModule_GetFilenameObject(v);
    if (pkgname == NULL) {
        pkgname_or_unknown = PyUnicode_FromString("<unknown module name>");
        if (pkgname_or_unknown == NULL) {
            Py_XDECREF(pkgpath);
            return NULL;
        }
    } else {
        pkgname_or_unknown = pkgname;
    }

    if (pkgpath == NULL || !PyUnicode_Check(pkgpath)) {
        _PyErr_Clear(tstate);
        errmsg = PyUnicode_FromFormat(
            "cannot import name %R from %R (unknown location)",
            name, pkgname_or_unknown
        );
        /* NULL checks for errmsg and pkgname done by PyErr_SetImportError. */
        _PyErr_SetImportErrorWithNameFrom(errmsg, pkgname, NULL, name);
    }
    else {
        PyObject *spec = PyObject_GetAttr(v, &_Py_ID(__spec__));
        const char *fmt =
            _PyModuleSpec_IsInitializing(spec) ?
            "cannot import name %R from partially initialized module %R "
            "(most likely due to a circular import) (%S)" :
            "cannot import name %R from %R (%S)";
        Py_XDECREF(spec);

        errmsg = PyUnicode_FromFormat(fmt, name, pkgname_or_unknown, pkgpath);
        /* NULL checks for errmsg and pkgname done by PyErr_SetImportError. */
        _PyErr_SetImportErrorWithNameFrom(errmsg, pkgname, pkgpath, name);
    }

    Py_XDECREF(errmsg);
    Py_XDECREF(pkgname_or_unknown);
    Py_XDECREF(pkgpath);
    return NULL;
}
```


為什麼 x 為 NULL 卻沒噴 Error？

簡答：其實有但被清掉了。

詳答 TODO，原始碼追下去就知道了。



#### 2. AttributeError

也是呼叫了 `_PyModuleSpec_IsInitializing(spec)` 來變化錯誤訊息，
確認等同於 `ModuleSpec._initializing`。
到此算是驗證完成。


https://github.com/python/cpython/blob/a030bae5/Objects/moduleobject.c#L827-L833
```c
PyObject*
_Py_module_getattro_impl(PyModuleObject *m, PyObject *name, int suppress)
{
    // ...
            if (_PyModuleSpec_IsInitializing(spec)) {
                PyErr_Format(PyExc_AttributeError,
                                "partially initialized "
                                "module '%U' has no attribute '%U' "
                                "(most likely due to a circular import)",
                                mod_name, name);
            }
            else if (_PyModuleSpec_IsUninitializedSubmodule(spec, name)) {
                PyErr_Format(PyExc_AttributeError,
                                "cannot access submodule '%U' of module '%U' "
                                "(most likely due to a circular import)",
                                name, mod_name);
            }
            else {
                PyErr_Format(PyExc_AttributeError,
                                "module '%U' has no attribute '%U'",
                                mod_name, name);
            }

    // ...   
}
```



### 來看看 Git log 有沒有解釋 `ModuleSpec._initializing`

以目前所知，有 2 個可下手的地方：
-   Python `ModuleSpec._initializing` 賦值的地方
-   C function `_PyModuleSpec_IsInitializing(spec)`



#### Git log - `ModuleSpec._initializing` 賦值的地方

`spec._initializing = True`
-   https://github.com/python/cpython/blob/a030bae5/Lib/importlib/_bootstrap.py#L926

`spec._initializing = False`
-   https://github.com/python/cpython/blob/a030bae5/Lib/importlib/_bootstrap.py#L950


用 Git blame 追下去，在 PyCharm 對原始碼行號右鍵「Annotate with Git Blame」，
往前追了好幾次，這邊列出重要的轉變：
-   b523f843 2013/11/23 00:05 Eric Snow Implement PEP 451 (ModuleSpec).
-   4f0338ca 2012/8/28 06:24 Antoine Pitrou Issue #15781: Fix two small race conditions in import's module locking. 
-   ea3eb88b 2012/5/18 00:55 Antoine Pitrou Issue #9260: A finer-grained import lock.


「ea3eb88b A finer-grained import lock」牽涉到 Global Import Lock（GIL），
為了理解 GIL 的起源及職責範圍，
因此發現在早期（1998/3/4）就已提到「partially initialized module」。
-   75acc9ca 1998/3/4 06:26 Guido van Rossum Add a single Python-wide (!) lock on import.
    Only one thread at a time can be in PyImport_ImportModuleEx().
    Recursive calls from the same thread are okay.


雖然討論串、文件中沒直接說明 `ModuleSpec._initializing`，
但從上列原始碼看下來，能體會用意，請見後續段落說明。



###### b523f843 2013/11/23 00:05 Eric Snow Implement PEP 451 (ModuleSpec).

https://github.com/python/cpython/issues/63064  
https://bugs.python.org/issue18864#msg202655
```
2. change module.__initializing__ to module.__spec__._initializing
```



###### 4f0338ca 2012/8/28 06:24 Antoine Pitrou Issue #15781: Fix two small race conditions in import's module locking.

https://github.com/python/cpython/issues/59985  
https://bugs.python.org/issue15781#msg169217
```
Here is a patch. 
There was a race between putting the new module in sys.modules and setting its __initializing__ attribute, 
so now __initializing__ is set before putting the module in sys.modules.
```



###### ea3eb88b 2012/5/18 00:55 Antoine Pitrou Issue #9260: A finer-grained import lock.

https://github.com/python/cpython/issues/53506  
https://bugs.python.org/issue9260


這個 commit 新增了 `module.__initializing__`，
在 `loader.load_module()` 之前與之後對其賦值，
它以 True、False 分別代表載入模組原始碼的開始與結束。

並用在 C API `PyImport_ImportModuleLevelObject()` 中：  
在 import 過程中，操作模組物件之前必須取得模組鎖（請見後續段落說明本 commit），
當欲 import 的模組已存於 `sys.modules` 且已完成初始化，
就不需要再對該模組物件進行多餘的操作（連帶牽涉模組鎖）；
故以 `module.__initializing__` 判斷，
當模組正在初始化時，我們所需要做的就是等待直到它完成。

如何進行等待？  
在模組鎖上鎖的情況下，
若再度上鎖的人（執行緒）不同於原上鎖人，則再度上鎖的人會被 blocking 直到鎖被釋放，
但是，若預判上鎖將發生 deadlock，則放棄上鎖以避免之。
這就是 `_bootstrap._lock_unlock_module()` 的運作──上鎖後緊接著解鎖，
該函式會 blocking 直到該模組被完整 import 後鎖被釋放，
才能真的上鎖再解鎖，
這種 blocking 就是等待。

總結 import 模組得到「partially initialized module」的情況有：
-   相同執行緒的 Circular Import
-   不同執行緒的 Circular Import 但為了避免 deadlock


https://github.com/python/cpython/commit/ea3eb88b?diff=unified&w=0#diff-dba786ae26d5505c4c367a93b1179c2f80f2433d983b84bacb9001fb552f0761R406
```py
def module_for_loader(fxn):
    def module_for_loader_wrapper(self, fullname, *args, **kwargs):
        module = sys.modules.get(fullname)
        is_reload = module is not None
        if not is_reload:
            module = new_module(fullname)
            sys.modules[fullname] = module
            # ...
        try:
            module.__initializing__ = True
            # If __package__ was not set above, __import__() will do it later.
            return fxn(self, module, *args, **kwargs)
        except:
            if not is_reload:
                del sys.modules[fullname]
            raise
        finally:
            module.__initializing__ = False
    _wrap(module_for_loader_wrapper, fxn)
    return module_for_loader_wrapper
```


https://github.com/python/cpython/blob/ea3eb88b/Lib/importlib/_bootstrap.py#L617
```py
class _LoaderBasics:
    
    @module_for_loader
    def _load_module(self, module, *, sourceless=False):
        # ...
        return module
```


https://github.com/python/cpython/blob/ea3eb88b/Lib/importlib/_bootstrap.py#L746
```py
class SourceLoader(_LoaderBasics):

    def load_module(self, fullname):
        return self._load_module(fullname)
```


https://github.com/python/cpython/commit/ea3eb88b?diff=unified&w=0#diff-28cfc3e2868980a79d93d2ebdc8747dcb9231f3dd7f2caef96e74107d1ea3bf3R1586
```c
PyObject *
PyImport_ImportModuleLevelObject(PyObject *name, PyObject *given_globals,
                                 PyObject *locals, PyObject *given_fromlist,
                                 int level)
{
    // ...
    
    mod = PyDict_GetItem(interp->modules, abs_name);
    if (mod == Py_None) {
        // ...
    }
    else if (mod != NULL) {
        PyObject *value;
        int initializing = 0;

        Py_INCREF(mod);
        /* Only call _bootstrap._lock_unlock_module() if __initializing__ is true. */
        value = _PyObject_GetAttrId(mod, &PyId___initializing__);
        if (value == NULL)
            PyErr_Clear();
        else {
            initializing = PyObject_IsTrue(value);
            Py_DECREF(value);
            if (initializing == -1)
                PyErr_Clear();
        }
        if (initializing > 0) {
            /* _bootstrap._lock_unlock_module() releases the import lock */
            value = _PyObject_CallMethodObjIdArgs(interp->importlib,
                                            &PyId__lock_unlock_module, abs_name,
                                            NULL);
            if (value == NULL)
                goto error;
            Py_DECREF(value);
        }
        else {
#ifdef WITH_THREAD
            if (_PyImport_ReleaseLock() < 0) {
                PyErr_SetString(PyExc_RuntimeError, "not holding the import lock");
                goto error;
            }
#endif
        }        
    }
    else {
        /* _bootstrap._find_and_load() releases the import lock */
        mod = _PyObject_CallMethodObjIdArgs(interp->importlib,
                                            &PyId__find_and_load, abs_name,
                                            builtins_import, NULL);
        if (mod == NULL) {
            goto error;
        }
    }
    
    // ...    
}
```


https://github.com/python/cpython/commit/ea3eb88b?diff=unified&w=0#diff-dba786ae26d5505c4c367a93b1179c2f80f2433d983b84bacb9001fb552f0761R282
```py
def _lock_unlock_module(name):
    """Release the global import lock, and acquires then release the
    module lock for a given module name.
    This is used to ensure a module is completely initialized, in the
    event it is being imported by another thread.
    Should only be called with the import lock taken."""
    lock = _get_module_lock(name)
    _imp.release_lock()
    try:
        lock.acquire()
    except _DeadlockError:
        # Concurrent circular import, we'll accept a partially initialized
        # module object.
        pass
    else:
        lock.release()
```



這個 commit 在專用於 import 的「鎖的機制」，寫下歷史的新頁！  
下列簡述來龍去脈：

這個 commit 起因於
當時的 import 機制皆仰賴一個 Global Import Lock（GIL），
在某些狀況會發生 deadlock，
於是開始討論如何把鎖的粒度做得更細緻，
減少不必要的 blocking 以避免 deadlock。
（詳見討論串 [Import lock knowledge required!](https://mail.python.org/pipermail/python-dev/2003-February/033436.html) ）

最後這個 commit 實作了一種 Reentrant Lock （`_ModuleLock`），
大幅地分擔了 Global Import Lock 的職責，
每個被 import 的模組各有一把鎖，並以模組名稱來辨識鎖，本文以「模組鎖」稱之。
接下來簡述 import 模組的流程變化，
首先使用 GIL 取得模組鎖物件後釋放 GIL，
然後必須持有（鎖住）模組鎖才能操作該模組物件進行後續既有的 import 流程。
（詳見本 commit bpo-9260 討論串：
[#msg110287](https://bugs.python.org/issue9260#msg110287)
、[#msg150322](https://bugs.python.org/issue9260#msg150322)
、[#msg160205](https://bugs.python.org/issue9260#msg160205)）

粒度的變化可見 [Lib/importlib/_bootstrap.py](https://github.com/python/cpython/commit/ea3eb88b?diff=split&w=0#diff-dba786ae26d5505c4c367a93b1179c2f80f2433d983b84bacb9001fb552f0761)： 
-   `_gcd_import()`： GIL 鎖一整塊 -> 切細再鎖
-   `_lock_unlock_module()`： 使用 GIL 取得模組鎖物件後，改用模組鎖
-   `_find_and_load()`： 使用 GIL 取得模組鎖物件後，改用模組鎖
-   `_find_module()`： 只在 `loader = finder.find_module(name, path)` 使用 GIL



鎖的機制可以 **稍微** 參考下列這篇流程圖（基於 CPython v3.8.0a0）  
https://github.com/zpoint/CPython-Internals/blob/a19f7a9/Interpreter/module/module.md#how-does-import-work

CPython v3.8.0a0 原始碼  
https://github.com/python/cpython/tree/ab54b9a



###### 75acc9ca 1998/3/4 06:26 Guido van Rossum Add a single Python-wide (!) lock on import.

https://github.com/python/cpython/commit/75acc9ca


西元 1998 年 3 月大約是正在開發 v1.5.1。
找不到開發討論串，
已找過：
-   Mailing Lists：
    [Python-Dev](https://mail.python.org/pipermail/python-dev/)
    、[Python-checkins](https://mail.python.org/pipermail/python-checkins/)
    、[Python-announce](https://mail.python.org/pipermail/python-announce-list/)
-   BPO
-   [PEP](https://peps.python.org/pep-0000/)
-   GitHub issues/PRs


https://github.com/python/cpython/commit/75acc9ca#diff-28cfc3e2868980a79d93d2ebdc8747dcb9231f3dd7f2caef96e74107d1ea3bf3R116-R118
```c
/* Locking primitives to prevent parallel imports of the same module
   in different threads to return with a partially loaded module.
   These calls are serialized by the global interpreter lock. */

#ifdef WITH_THREAD

#include "thread.h"

static type_lock import_lock = 0;
static long import_lock_thread = -1;
static int import_lock_level = 0;

static void
lock_import()
{
	long me = get_thread_ident();
	if (me == -1)
		return; /* Too bad */
	if (import_lock == NULL)
		import_lock = allocate_lock();
	if (import_lock_thread == me) {
		import_lock_level++;
		return;
	}
	if (import_lock_thread != -1 || !acquire_lock(import_lock, 0)) {
		PyThreadState *tstate = PyEval_SaveThread();
		acquire_lock(import_lock, 1);
		PyEval_RestoreThread(tstate);
	}
	import_lock_thread = me;
	import_lock_level = 1;
}

static void
unlock_import()
{
	long me = get_thread_ident();
	if (me == -1)
		return; /* Too bad */
	if (import_lock_thread != me)
		Py_FatalError("unlock_import: not holding the import lock");
	import_lock_level--;
	if (import_lock_level == 0) {
		import_lock_thread = -1;
		release_lock(import_lock);
	}
}

#else

#define lock_import()
#define unlock_import()

#endif
```



#### Git log - `_PyModuleSpec_IsInitializing(spec)`

首先，尋找它最一開始被新增進去的 commit，看有沒有線索能找到它的解釋。

拜 PyCharm 內建 Git 功能的開發團隊優秀所賜，
選取整個 function 後，右鍵「Git > Show History for Selection...」
能顯示這個 function 的所有 commit。
縱使 function 名稱曾變動過（在選取範圍內）也不需再次往前追，
這方法很適合歷史悠久的專案。

一下子就找到線索了！
-   3e429dcc 2018/10/30 19:19 Serhiy Storchaka bpo-33237: Improve AttributeError message for partially initialized module. (GH-6398)

上列 PR 合併後陸續有人提出相關的 PR 並關聯至原 PR
-   65366bc8 2019/9/9 23:17 Anthony Sottile bpo-20490: Improve circular import error message (GH-15308)


最後，看完上列原始碼、討論串沒有找到解釋，
他們都直接把別處既有的邏輯搬過來用，沒有進一步解釋。



###### 3e429dcc 2018/10/30 19:19 Serhiy Storchaka bpo-33237: Improve AttributeError message for partially initialized module. (GH-6398)

https://github.com/python/cpython/issues/77418  
https://bugs.python.org/issue33237#msg315020  
https://github.com/python/cpython/pull/6398
 

這個 commit 新增了 `_PyModuleSpec_IsInitializing(spec)`。
改善錯誤訊息的判斷邏輯從 `PyImport_ImportModuleLevelObject()` 中複製過來用，
覺得重複的程式碼太冗長了，
於是抽出來寫成一個函式
（[bpo-33237#msg315136](https://bugs.python.org/issue33237#msg315136)）。


這是本文所提的第 2 種 Circular Import Error 的出處。


https://github.com/python/cpython/commit/3e429dcc?diff=unified&w=0#diff-8c2a0fd137780a0ee11c19aae8e46e8490f7667698cd78a5bde466bc995a08c5R705
```c
/* Check if the "_initializing" attribute of the module spec is set to true.
   Clear the exception and return 0 if spec is NULL.
 */
int
_PyModuleSpec_IsInitializing(PyObject *spec)
{
    if (spec != NULL) {
        _Py_IDENTIFIER(_initializing);
        PyObject *value = _PyObject_GetAttrId(spec, &PyId__initializing);
        if (value != NULL) {
            int initializing = PyObject_IsTrue(value);
            Py_DECREF(value);
            if (initializing >= 0) {
                return initializing;
            }
        }
    }
    PyErr_Clear();
    return 0;
}
```


https://github.com/python/cpython/commit/3e429dcc?diff=unified&w=0#diff-8c2a0fd137780a0ee11c19aae8e46e8490f7667698cd78a5bde466bc995a08c5R745-R751
```c
static PyObject*
module_getattro(PyModuleObject *m, PyObject *name)
{
    // ...
            if (_PyModuleSpec_IsInitializing(spec)) {
                PyErr_Format(PyExc_AttributeError,
                             "partially initialized "
                             "module '%U' has no attribute '%U' "
                             "(most likely due to a circular import)",
                             mod_name, name);
            }
            else {
                PyErr_Format(PyExc_AttributeError,
                             "module '%U' has no attribute '%U'",
                             mod_name, name);
            }
    // ...
}
```


https://github.com/python/cpython/commit/3e429dcc?diff=unified&w=0#diff-28cfc3e2868980a79d93d2ebdc8747dcb9231f3dd7f2caef96e74107d1ea3bf3R1733-R1742
```c
PyObject *
PyImport_ImportModuleLevelObject(PyObject *name, PyObject *globals,
                                 PyObject *locals, PyObject *fromlist,
                                 int level)
{
    // ...
    mod = PyImport_GetModule(abs_name);
    if (mod != NULL && mod != Py_None) {
    
        // ...
    
        if (_PyModuleSpec_IsInitializing(spec)) {
            PyObject *value = _PyObject_CallMethodIdObjArgs(interp->importlib,
                                            &PyId__lock_unlock_module, abs_name,
                                            NULL);
            if (value == NULL) {
                Py_DECREF(spec);
                goto error;
            }
            Py_DECREF(value);
        }    
    // ...
}
```



###### 65366bc8 2019/9/9 23:17 Anthony Sottile bpo-20490: Improve circular import error message (GH-15308)

https://github.com/python/cpython/issues/64689  
https://bugs.python.org/issue20490  
https://github.com/python/cpython/pull/15308  
https://github.com/python/cpython/pull/15791 (backport this PR to v3.8，程式碼都一樣)  


https://github.com/python/cpython/pull/15308/#issuecomment-521773359
```
This is largely based on the work in https://bugs.python.org/issue33237 by @serhiy-storchaka #6398
```


這是本文所提的第 1 種 Circular Import Error 的出處。


