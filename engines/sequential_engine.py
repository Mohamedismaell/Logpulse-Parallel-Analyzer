import time
from core.parsing import parse_file
from core.domain import AnalyzerCore, AnalysisResult

class SequentialEngine:
    
    @staticmethod
    def run_analysis(files, keyword="", check_cancel=None, progress_cb=None) -> AnalysisResult:
        start = time.perf_counter()
        all_errors = []
        global_freq = {}
        total = len(files)
        
        for i, path in enumerate(files):
            if check_cancel and check_cancel():
                return AnalysisResult(0.0, 0, [], {})
                
            entries = parse_file(path, keyword)
            errors, freq = AnalyzerCore.process_entries(entries, check_cancel)
            
            all_errors.extend(errors)
            for k, v in freq.items():
                global_freq[k] = global_freq.get(k, 0) + v
                
            if progress_cb:
                progress_cb(i + 1, total)
                
        t = time.perf_counter() - start
        return AnalyzerCore.compile_results(all_errors, global_freq, t)
