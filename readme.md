# [DmitryKuk](https://github.com/DmitryKuk) / [asynchronizer](https://github.com/DmitryKuk/asynchronizer)
#### Python asyncio <-> Boost.Asio bridge
---

# What is this?
asynchronizer is a simple bridge for synchronization between [Boost.Asio](https://www.boost.org/doc/libs/1_69_0/doc/html/boost_asio.html) and [Python 3 asyncio](https://docs.python.org/3/library/asyncio.html). It provides small Python extension (using [pybind11](https://github.com/pybind/pybind11)) and Python wrapper.

# What is it for?
- You write complex application with asynchronous C++ code and want to use some Python to simplify this challenge.
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
**Note:** Using Python `venv` is recommended.
1. Install Python dependencies:
```
pip install -r requirements.txt
```
**Note:** Install dependencies for testing, if you want run tests:
```
pip install -r testing-requirements.txt
```
2. Build Python extension and stub:
```
b2
```
3. Install `asynchronizer.py`, Python extension and stub for it into current `site-packages` directory:
```
b2 install
```
4. Run some tests, if you want:
```
b2 install-test-async-sleep-ext
PYTHONPATH="$( pwd )/build/ext:$PYTHONPATH" pytest
```

# Using in your project
Just write your modules using pybind11 as usual!

Wrap your asynchronous code like [ext_src/test_async_sleep_ext.cpp](ext_src/test_async_sleep_ext.cpp) does.

**Note:** `asynchronizer` (with some pybind11 magic) provides bindings for some Boost.Asio, so it's enough to import `IoContext` and other from installed `asynchronizer` module in your Python code: you are not required to copy `IoContext` wrapper bindings into your project.

**Optional:** If your code require `std::shared_ptr`-managed classes, you can:
1. use directory `include` in header search path in your project
2. do this in your project:
    ```
    #include <dkuk/asynchronizer/asynchronizer.hpp>

    PYBIND11_MODULE(my_module, module)
    {
        ...
        dkuk::asynchronizer::shared_ptr_managed_class<my_class>{module, "MyClass"};
        ...
    }
    ```

# Examples
See [tests](tests).

---

Author: [Dmitry Kukovinets](https://github.com/DmitryKuk), <d1021976@gmail.com>, 16.03.2019 10:18
