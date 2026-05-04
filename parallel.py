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

def run_analysis(files, check_cancel=None, progress_cb=None):
    """
    Runs parallel log analysis on a list of files.
    Returns: (total_time_seconds, total_errors, most_common_list, errors_per_minute_dict)
    """
    start = time.perf_counter()
    total = len(files)
    
    with multiprocessing.Pool() as pool:
        # Launching tasks individually explicitly helps us poll accurate individual real-time completion
        results = [pool.apply_async(_worker, (f,)) for f in files]
        
        last_completed = -1
        while True:
            if check_cancel and check_cancel():
                pool.terminate()
                return 0.0, 0, [], {}
                
            completed = sum(1 for r in results if r.ready())
            
            # Fire progress updates only when integers advance
            if completed != last_completed and progress_cb:
                progress_cb(completed, total)
                last_completed = completed
                
            if completed == total:
                break
                
            time.sleep(0.1)

    all_errors = []
    for r in results:
        all_errors.extend(r.get())

    msgs = [m for _, m in all_errors]
    c = Counter(msgs)
    freq = defaultdict(int)
    for t, _ in all_errors:
        minute = t[:16]
        freq[minute] += 1

    t = time.perf_counter() - start
    return round(t, 2), len(all_errors), c.most_common(3), dict(freq)