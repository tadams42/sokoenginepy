# pip install -U memory_profile
# python -m memory_profiler memprof.py

import sokoenginepy

@profile
def my_func():
    l = 10000000 * [sokoenginepy.AtomicMove()]
    return l


if __name__ == '__main__':
    my_func()
