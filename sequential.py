import time
import re
from collections import Counter, defaultdict

def run_analysis(files, check_cancel=None, progress_cb=None):
    """
    Runs sequential log analysis on a list of files.
    Returns: (total_time_seconds, total_errors, most_common_list, errors_per_minute_dict)
    """
    start = time.perf_counter()
    pattern = r"\[(.*?)\] (\w+): (.*)"
    all_errors = []
    
    total = len(files)
    for i, path in enumerate(files):
        if check_cancel and check_cancel():
            return 0.0, 0, [], {}
            
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if check_cancel and check_cancel():
                    return 0.0, 0, [], {}
                    
                m = re.match(pattern, line)
                if m:
                    t, lvl, msg = m.groups()
                    if lvl == "ERROR":
                        all_errors.append((t, msg))
                        # Simulate heavy hashing workload
                        for _ in range(15000):
                            x = hash(msg)
                            x = x * x
                            
        # Report progress dynamically outside the line loop per file
        if progress_cb:
            progress_cb(i + 1, total)
                            
    msgs = [m for _, m in all_errors]
    c = Counter(msgs)
    freq = defaultdict(int)
    for t, _ in all_errors:
        minute = t[:16] # Extract "YYYY-MM-DD HH:MM"
        freq[minute] += 1
        
    t = time.perf_counter() - start
    return round(t, 2), len(all_errors), c.most_common(3), dict(freq)