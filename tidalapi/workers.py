import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

log = logging.getLogger(__name__)


def func_wrapper(args):
    """
    args: tuple(func, limit, offset, *extra_args)
    Returns list of (index, item)
    """
    func, limit, offset, *extra_args = args
    try:
        items = func(limit, offset, *extra_args)
    except Exception as e:
        log.error(
            "Failed to run %s(limit=%d, offset=%d, args=%s)",
            func,
            limit,
            offset,
            extra_args,
        )
        log.exception(e)
        items = []

    return [(i + offset, item) for i, item in enumerate(items)]


def get_items(
    func: Callable,
    total_count: int,
    *args,
    parse: Callable = lambda _: _,
    chunk_size: int = 50,
    processes: int = 2,
):
    """This function performs pagination on a function that supports `limit`/`offset`
    parameters and it runs API requests in parallel to speed things up."""
    offsets = list(range(0, total_count, chunk_size))
    items = []

    with ThreadPoolExecutor(processes) as pool:
        args_list = [(func, chunk_size, offset, *args) for offset in offsets]

        for page_items in pool.map(func_wrapper, args_list):
            items.extend(page_items)

    items = [item for _, item in sorted(items, key=lambda x: x[0])]
    return list(map(parse, items))
