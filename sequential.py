import time
import re
from collections import Counter, defaultdict

def run_analysis(files, check_cancel=None):
    start = time.perf_counter()
    pattern = r"\[(.*?)\] (\w+): (.*)"
    all_errors = []
    
    for path in files:
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
                            
    msgs = [m for _, m in all_errors]
    c = Counter(msgs)
    freq = defaultdict(int)
    for t, _ in all_errors:
        minute = t[:16] 
        freq[minute] += 1
        
    t = time.perf_counter() - start
    return round(t, 2), len(all_errors), c.most_common(3), dict(freq)