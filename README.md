# Cache

`cache.py` is a simple python file that extends meomization across runs using a cache file.

Why?  Often it takes some time to load files, do expensive data processing, and train models.
As a result, many nice interfaces have popped up to make the experience smoother, like Jupyter notebooks.
However, these interfaces make it somewhat hard to keep coding conventions clean and develop a library.

`cache.py` attempts to make it painless to cache the expensive functions in your program to disk,
allowing quick iteration while developing usable code.

# Usage

To use the file, `import cache` and annotate functions with `@cache.cache()`.

```python
import cache

@cache.cache()
def expensive_func(arg, kwarg=None):
  # Expensive stuff here
  return arg

```

The `@cache.cache()` function can take multiple arguments.

- `@cache.cache(timeout=20)` - Only caches the function for 20 seconds.
- `@cache.cache(fname="my_cache.pkl")` - Saves cache to a custom filename (defaults to hidden file `.cache.pkl`
- `@cache.cache(key=ARGS[KWARGS,NONE])` - Check against args, kwargs or neither of them when doing a cache lookup.

# How it works

With a file loaded from disk, `cache.py` checks against the name, arguments and hash of a function's source
to decide if the function has been run before.  If it has it returns the cached result immediately.
It uses `pickle` and `inspect` under the hood, making it currently non-portable.
