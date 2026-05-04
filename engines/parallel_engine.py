import multiprocessing
import time
from core.parsing import parse_file
from core.domain import AnalyzerCore, AnalysisResult

def _worker(args):
    path, keyword = args
    entries = parse_file(path, keyword)
    return AnalyzerCore.process_entries(entries)

class ParallelEngine:
    
    @staticmethod
    def run_analysis(files, keyword="", check_cancel=None, progress_cb=None) -> AnalysisResult:
        start = time.perf_counter()
        total = len(files)
        
        args = [(f, keyword) for f in files]
        
        with multiprocessing.Pool() as pool:
            results = [pool.apply_async(_worker, (arg,)) for arg in args]
            
            last_completed = -1
            while True:
                if check_cancel and check_cancel():
                    pool.terminate()
                    return AnalysisResult(0.0, 0, [], {})
                    
                completed = sum(1 for r in results if r.ready())
                
                if completed != last_completed and progress_cb:
                    progress_cb(completed, total)
                    last_completed = completed
                    
                if completed == total:
                    break
                    
                time.sleep(0.1)
                
        all_errors = []
        global_freq = {}
        for r in results:
            errors, freq = r.get()
            all_errors.extend(errors)
            for k, v in freq.items():
                global_freq[k] = global_freq.get(k, 0) + v
                
        t = time.perf_counter() - start
        return AnalyzerCore.compile_results(all_errors, global_freq, t)
