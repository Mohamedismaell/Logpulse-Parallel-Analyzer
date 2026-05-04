from dataclasses import dataclass
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str

@dataclass
class AnalysisResult:
    time_taken: float
    total_errors: int
    most_common: List[Tuple[str, int]]
    freq_per_minute: Dict[str, int]

class AnalyzerCore:
    """Core domain logic representing our rules for error evaluation and processing."""
    
    @staticmethod
    def process_entries(entries: List[LogEntry], check_cancel=None) -> Tuple[List[LogEntry], Dict[str, int]]:
        error_entries = []
        freq = defaultdict(int)
        
        for e in entries:
            if check_cancel and check_cancel():
                break
                
            if e.level == "ERROR":
                error_entries.append(e)
                minute = e.timestamp[:16]
                freq[minute] += 1
                
                # Heavy workload simulation to evaluate parallel speeds
                for _ in range(5000):
                    x = hash(e.message) * hash(e.message)
                    
        return error_entries, dict(freq)
        
    @staticmethod
    def compile_results(errors: List[LogEntry], freq: Dict[str, int], time_taken: float) -> AnalysisResult:
        msgs = [e.message for e in errors]
        c = Counter(msgs)
        return AnalysisResult(
            time_taken=round(time_taken, 2),
            total_errors=len(errors),
            most_common=c.most_common(5),
            freq_per_minute=freq
        )
