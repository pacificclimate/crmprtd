import logging
from types import SimpleNamespace


def sanitize_connection(sesh):
    return sesh.bind.url.render_as_string(hide_password=True)


def cached_function(attrs):
    """A decorator factory that can be used to cache database results
    Neither database sessions (i.e. the sesh parameter of each wrapped
    function) nor SQLAlchemy mapped objects (the results of queries) are
    cachable or reusable. Therefore one cannot memoize database query
    functions using builtin things like the lrucache.
    This wrapper works, by a) assuming that the wrapped function's first
    argument is a database session b) assuming that the result of the
    query returns a single SQLAlchemy object (e.g. a History instance),
    and c) accepting as a parameter a list of attributes to retrieve and
    store in the cache result.
    args (except sesh) and kwargs to the wrapped function are used as
    the cache key, and results are the parametrized object attributes.
    """
    log = logging.getLogger(__name__)

    def wrapper(f):
        cache = {}

        def memoize(sesh, *args, **kwargs):
            nonlocal cache
            key = (args) + tuple(kwargs.items())
            if key not in cache:
                obj = f(sesh, *args, **kwargs)
                log.debug(
                    f"Cache miss: {f.__name__} {key} -> {repr(obj)}",
                    extra={"database": sanitize_connection(sesh)},
                )
                cache[key] = obj and SimpleNamespace(
                    **{attr: getattr(obj, attr) for attr in attrs}
                )
            return cache[key]

        return memoize

    return wrapper
