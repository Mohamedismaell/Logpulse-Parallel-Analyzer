import json
import re
from typing import List
from core.domain import LogEntry

def normalize_message(msg: str) -> str:
    """Normalizes dynamic structures so distinct system anomalies can securely be grouped by root cause."""
    msg = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '<IP>', msg)
    msg = re.sub(r'0x[0-9a-fA-F]+', '<HEX>', msg)
    msg = re.sub(r'\b\d+\b', '<NUM>', msg)
    return msg

def parse_file(filepath: str, keyword: str = "") -> List[LogEntry]:
    """IO bound parsing handler capable of decoding multi-line strings, JSON limits, and plain text simultaneously."""
    entries = []
    pattern = re.compile(r"\[(.*?)\] (\w+): (.*)")
    current_entry = None
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line: continue
            
            # 1. Advanced JSON Support Detection
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    t = data.get("timestamp", "")
                    lvl = data.get("level", "")
                    msg = data.get("message", "")
                    
                    if not isinstance(msg, str): continue
                    msg = normalize_message(msg)
                    
                    if keyword and keyword.lower() not in msg.lower(): continue
                    entries.append(LogEntry(t, lvl, msg))
                except json.JSONDecodeError:
                    pass
                continue
            
            # 2. Base Plain Text
            m = pattern.match(line)
            if m:
                # Flush previous multiline stack if any
                if current_entry:
                    msg = normalize_message(current_entry.message)
                    if not keyword or keyword.lower() in msg.lower():
                        current_entry.message = msg
                        entries.append(current_entry)
                        
                t, lvl, msg = m.groups()
                current_entry = LogEntry(t, lvl, msg)
            else:
                # 3. Multi-line Exception Routing (Stack Traces!)
                if current_entry:
                    current_entry.message += f"\n  {line}"
                    
        # Conclude last hanging file evaluation logic
        if current_entry:
            msg = normalize_message(current_entry.message)
            if not keyword or keyword.lower() in msg.lower():
                current_entry.message = msg
                entries.append(current_entry)
                
    return entries
