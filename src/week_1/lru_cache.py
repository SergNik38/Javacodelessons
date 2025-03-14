import unittest.mock
from collections import OrderedDict


def lru_cache(*args, maxsize=None):
    def create_wrapper(func, cache_obj, has_maxsize=False):
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key in cache_obj:
                if has_maxsize:
                    cache_obj.move_to_end(key)
                return cache_obj[key]

            result = func(*args, **kwargs)
            cache_obj[key] = result

            if has_maxsize and len(cache_obj) > maxsize:
                cache_obj.popitem(last=False)

            return result
        return wrapper

    if not maxsize:
        if args:
            func = args[0]
            cache = {}
            return create_wrapper(func, cache)

    def decorator(func):
        cache = OrderedDict()
        return create_wrapper(func, cache, has_maxsize=True)

    return decorator


@lru_cache
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
