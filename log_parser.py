import re
from typing import List, Dict, Any
from datetime import datetime

class LogParser:
    def __init__(self, log_format="apache_common") :
        self.log_format = log_format
        
        # Apache Common Log Format pattern
        self.apache_pattern = r'(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (.*?) (\S+)" (\d+) (\S+)'
        
        # Apache Combined Log Format pattern (Common + referrer and user agent)
        self.apache_combined_pattern = r'(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (.*?) (\S+)" (\d+) (\S+) "(.*?)" "(.*?)"'
    
    def parse_line(self, line: str) -> Dict[str, Any]:
        """Parse a single log line into a structured dictionary."""
        if self.log_format == "apache_common":
            match = re.match(self.apache_pattern, line)
            if match:
                ip, _, user, timestamp, method, path, protocol, status, size = match.groups()
                return {
                    "ip": ip,
                    "user": user,
                    "timestamp": timestamp,
                    "method": method,
                    "path": path,
                    "protocol": protocol,
                    "status": int(status),
                    "size": size if size != "-" else 0,
                    "raw": line
                }
        elif self.log_format == "apache_combined":
            match = re.match(self.apache_combined_pattern, line)
            if match:
                ip, _, user, timestamp, method, path, protocol, status, size, referrer, user_agent = match.groups()
                return {
                    "ip": ip,
                    "user": user,
                    "timestamp": timestamp,
                    "method": method,
                    "path": path,
                    "protocol": protocol,
                    "status": int(status),
                    "size": size if size != "-" else 0,
                    "referrer": referrer,
                    "user_agent": user_agent,
                    "raw": line
                }
        return {"raw": line, "parsed": False}
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse an entire log file."""
        parsed_logs = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parsed_line = self.parse_line(line.strip())
                if parsed_line.get("parsed", True):  # Only add successfully parsed lines
                    parsed_logs.append(parsed_line)
        return parsed_logs
