import multiprocessing
import time
import re
from collections import Counter, defaultdict

def _parse_log(path):
    pattern = r"\[(.*?)\] (\w+): (.*)"
    errors = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.match(pattern, line)
            if m:
                t, lvl, msg = m.groups()
                if lvl == "ERROR":
                    errors.append((t, msg))
                    for _ in range(15000):
                        x = hash(msg)
                        x = x * x
    return errors

def _worker(path):
    return _parse_log(path)

def run_analysis(files, check_cancel=None):
    start = time.perf_counter()
    
    with multiprocessing.Pool() as pool:
        res_async = pool.map_async(_worker, files)
        # Watch the async operation loop to check for cancel flags before blocking completely
        while not res_async.ready():
            if check_cancel and check_cancel():
                pool.terminate()
                return 0.0, 0, [], {}
            time.sleep(0.1)
        results = res_async.get()

    all_errors = []
    for r in results:
        all_errors.extend(r)

    msgs = [m for _, m in all_errors]
    c = Counter(msgs)
    freq = defaultdict(int)
    for t, _ in all_errors:
        minute = t[:16]
        freq[minute] += 1

    t = time.perf_counter() - start
    return round(t, 2), len(all_errors), c.most_common(3), dict(freq)