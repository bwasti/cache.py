import pickle
import time
import inspect
import base64
import hashlib


debug = False


def log(s):
    if debug:
        print(s)


caches = dict()
updated_caches = []


def get_cache(fname):
    if fname in caches:
        return caches[fname]
    try:
        with open(fname, "rb") as f:
            c = pickle.load(f)
    except:
        c = dict()
    caches[fname] = c
    return c


def write_to_cache(fname, obj):
    updated_caches.append(fname)
    caches[fname] = obj


def cleanup():
    for fname in updated_caches:
        with open(fname, "wb") as f:
            pickle.dump(caches[fname], f)


def get_fn_hash(f):
    return base64.b64encode(hashlib.sha1(inspect.getsource(f).encode("utf-8")).digest())


NONE = 0
ARGS = 1
KWARGS = 2


def cache(fname=".cache.pkl", timeout=-1, key=ARGS | KWARGS):

    def impl(fn):
        load_t = time.time()
        c = get_cache(fname)
        log("loaded cache in {:.2f}s".format(time.time() - load_t))

        def d(*args, **kwargs):
            log("checking cache on {}".format(fn.__name__))
            if key == ARGS | KWARGS:
                k = pickle.dumps((fn.__name__, args, kwargs))
            if key == ARGS:
                k = pickle.dumps((fn.__name__, args))
            if key == KWARGS:
                k = pickle.dumps((fn.__name__, kwargs))
            if key == NONE:
                k = pickle.dumps((fn.__name__))
            if k in c:
                h, t, to, res = c[k]
                if get_fn_hash(fn) == h and (to < 0 or (time.time() - t) < to):
                    log("cache hit.")
                    return res
            log("cache miss.")
            res = fn(*args, **kwargs)
            c[k] = (get_fn_hash(fn), time.time(), timeout, res)
            save_t = time.time()
            write_to_cache(fname, c)
            log("saved cache in {:.2f}s".format(time.time() - save_t))
            return res

        return d

    return impl


@cache(timeout=0.2)
def expensive(k):
    time.sleep(0.2)
    return k


@cache(key=KWARGS)
def expensive2(k, kwarg1=None):
    time.sleep(0.2)
    return k


def test():
    # Test timeout
    t = time.time()
    v = expensive(1)
    assert v == 1
    assert time.time() - t > 0.1
    t = time.time()
    expensive(1)
    assert time.time() - t < 0.1
    time.sleep(0.3)
    t = time.time()
    expensive(1)
    assert time.time() - t > 0.1
    t = time.time()
    v = expensive(2)
    assert v == 2
    assert time.time() - t > 0.1
    # Test key=_ annotation
    t = time.time()
    v = expensive2(2, kwarg1="test")
    assert v == 2
    assert time.time() - t > 0.1
    t = time.time()
    v = expensive2(1, kwarg1="test")
    assert v == 2
    assert time.time() - t < 0.1
    t = time.time()
    v = expensive2(1, kwarg1="test2")
    assert v == 1
    assert time.time() - t > 0.1
    cleanup()
    print("pass")


if __name__ == "__main__":
    test()
