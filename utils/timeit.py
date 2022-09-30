from functools import wraps
import time
import logging

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logging.info('Function ' + ''.join(func.__name__ ) + ' took ' + str(total_time) +  ' seconds')
        return result
    return timeit_wrapper
