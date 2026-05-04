import os
import random
from datetime import datetime, timedelta

def generate_test_logs(num_files=5, lines_per_file=3000):
    os.makedirs("test_logs", exist_ok=True)
    
    error_messages = [
        "Connection timeout reached!",
        "Failed to authenticate user token.",
        "NullReferenceException in rendering module.",
        "Database deadlock detected.",
        "Memory leak threshold exceeded."
    ]
    
    standard_messages = [
        "User successfully logged in.",
        "Server responded with 200 OK.",
        "Data synchronization completed.",
        "Cache flushed gracefully.",
        "Starting worker processes..."
    ]
    
    # Simulating logs starting from a specific date
    start_time = datetime(2024, 10, 25, 9, 0, 0)
    
    print("Generating log files. This may take a moment...\n")
    
    for i in range(1, num_files + 1):
        filename = f"test_logs/server_node_{i}.log"
        
        # Stagger the starting times slightly for different files
        current_time = start_time + timedelta(minutes=random.randint(1, 30))
        
        with open(filename, "w", encoding="utf-8") as f:
            for _ in range(lines_per_file):
                # 85% chance it's a normal log, 15% chance it's a critical ERROR
                if random.random() < 0.15:
                    lvl = "ERROR"
                    msg = random.choice(error_messages)
                else:
                    lvl = random.choice(["INFO", "DEBUG", "WARNING"])
                    msg = random.choice(standard_messages)
                
                # Advance time by a few seconds randomly to simulate real time passage
                current_time += timedelta(seconds=random.randint(1, 10))
                
                timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                # Applying the perfect formatting your system looks for!
                f.write(f"[{timestamp_str}] {lvl}: {msg}\n")
        
        print(f"Success -> {filename} generated with {lines_per_file} lines.")
        
if __name__ == "__main__":
    generate_test_logs(num_files=4, lines_per_file=5000)
    print("\nLog generation complete! You can open your App and upload the files inside the 'test_logs' directory.")
