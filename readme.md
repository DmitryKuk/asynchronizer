# [DmitryKuk](https://github.com/DmitryKuk) / [asyncronizer](https://github.com/DmitryKuk/asyncronizer)
#### Python asyncio <-> Boost.Asio bridge
---

# What is this?
asyncronizer is a simple bridge for syncronization between [Boost.Asio](https://www.boost.org/doc/libs/1_69_0/doc/html/boost_asio.html) and [Python 3 asyncio](https://docs.python.org/3/library/asyncio.html). It provides small Python extension (using [pybind11](https://github.com/pybind/pybind11)) and Python wrapper.

# What is it for?
- You write complex application with asyncronous C++ code and want to use some Python to simplify this challenge.
- You have awesome C++ library using Boost.Asio and want create Python bindings for it.

# License
MIT license. See [license.txt](license.txt).

# Requirements
- Compiler with C++14 support. For example, try `g++` of versions 5/6/... or modern `clang`.
- [Boost](http://www.boost.org/) (or just [Boost.Asio](https://www.boost.org/doc/libs/1_69_0/doc/html/boost_asio.html) and [Boost.System](https://www.boost.org/doc/libs/1_69_0/libs/system/doc/html/system.html)) (`>= 1.66.0` because of [Boost.Asio](http://www.boost.org/doc/libs/1_69_0/doc/html/boost_asio.html) refactoring since `1.65`)
    + *Tested: **Boost 1.68.0** on **Mac OS X 10.11***
- [Boost.Build](http://www.boost.org/build/) (or any other build system -- it's simple).
    + *Note: Set environment variable `BOOST_ROOT` to unpacked Boost directory path.*
- [Python](https://www.python.org) `>=3.6`
    + *Tested: **Python 3.6.4** on **Mac OS X 10.11***
- Some Python packages (usually installed by pip; see `Installation` section and files: [requirements.txt](requirements.txt), [testing-requirements.txt](testing-requirements.txt)).

# Installation
1. Install Python dependencies:
```
pip install -r requirements.txt
```
**Note:** Install dependencies for testing, if you want run tests:
```
pip install -r testing-requirements.txt
```
2. Build Python extension:
```
b2
```
3. Install Python extension and Python stubs for it into directory `build/ext`:
```
b2 install-ext install-stub
```
4. Run some tests, if you want:
```
PYTHONPATH="$( pwd )/build/ext:$PYTHONPATH" pytest
```
5. Copy asyncronizer directory and files `build/ext/*` into your `site-packages` directory or install just these files manually:
```
asyncronizer.py (+ __init__.py, if packed as directory)
build/ext/* (or just .so/.dll python extension)
```

# Using in your project
Just write your modules using pybind11 as usual!

Wrap your asynchronous code like [ext_src/test_async_sleep_ext.cpp](ext_src/test_async_sleep_ext.cpp) does.

**Note:** `asyncronizer` (with some pybind11 magic) provides bindings for some Boost.Asio, so it's enough to import `IoContext` and other from installed `asyncronizer` module in your Python code: you are not required to copy `IoContext` wrapper bindings into your project.

**Optional:** If your code require `std::shared_ptr`-managed classes, you can:
1. use directory `include` in header search path in your project
2. do this in your project:
    ```
    #include <dkuk/asyncronizer/asyncronizer.hpp>

    PYBIND11_MODULE(my_module, module)
    {
        ...
        dkuk::asyncronizer::shared_ptr_managed_class<my_class>{module, "MyClass"};
        ...
    }
    ```

# Examples
See [tests](tests).

---

Author: [Dmitry Kukovinets](https://github.com/DmitryKuk), <d1021976@gmail.com>, 16.03.2019 10:18
