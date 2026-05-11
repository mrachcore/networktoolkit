import re
from collections import Counter


IMPORTANT_KEYWORDS = ["ERROR", "WARNING", "FAILED", "DENIED"]
IP_PATTERN = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
WORD_PATTERN = r"\b[a-zA-Z]{4,}\b"


def analyze_log_text(log_text):
    """Analyze uploaded log text and return beginner-friendly statistics."""
    lines = log_text.splitlines()
    important_lines = find_important_lines(lines)
    ip_addresses = find_ip_addresses(log_text)
    common_words = find_common_words(log_text)

    return {
        "total_lines": len(lines),
        "keyword_counts": count_keywords(lines),
        "important_lines": important_lines,
        "common_ips": ip_addresses,
        "common_words": common_words,
    }


def count_keywords(lines):
    """Count important security/troubleshooting words in the log file."""
    counts = {}
    for keyword in IMPORTANT_KEYWORDS:
        counts[keyword] = sum(1 for line in lines if keyword in line.upper())

    return counts


def find_important_lines(lines):
    """Return log lines that contain one of the important keywords."""
    matches = []

    for line_number, line in enumerate(lines, start=1):
        upper_line = line.upper()
        if any(keyword in upper_line for keyword in IMPORTANT_KEYWORDS):
            matches.append({"line": line_number, "text": line})

    return matches


def find_ip_addresses(log_text, limit=10):
    """Find the most common IPv4 addresses in the log text."""
    candidates = re.findall(IP_PATTERN, log_text)

    # Validate each candidate so impossible addresses like 999.999.999.999 are ignored.
    valid_ips = []
    for ip_address in candidates:
        octets = ip_address.split(".")
        if all(0 <= int(octet) <= 255 for octet in octets):
            valid_ips.append(ip_address)

    return Counter(valid_ips).most_common(limit)


def find_common_words(log_text, limit=10):
    """Find common words while ignoring frequent log-level keywords."""
    words = [word.lower() for word in re.findall(WORD_PATTERN, log_text)]
    ignored_words = {"error", "warning", "failed", "denied", "info", "debug", "trace"}
    filtered_words = [word for word in words if word not in ignored_words]

    return Counter(filtered_words).most_common(limit)


def build_summary_text(analysis):
    """Create a plain text summary that can be downloaded from Streamlit."""
    keyword_counts = analysis["keyword_counts"]

    lines = [
        "Network Toolkit Log Analysis Summary",
        "====================================",
        f"Total lines: {analysis['total_lines']}",
        f"ERROR count: {keyword_counts.get('ERROR', 0)}",
        f"WARNING count: {keyword_counts.get('WARNING', 0)}",
        f"FAILED count: {keyword_counts.get('FAILED', 0)}",
        f"DENIED count: {keyword_counts.get('DENIED', 0)}",
        "",
        "Most common IP addresses:",
    ]

    if analysis["common_ips"]:
        for ip_address, count in analysis["common_ips"]:
            lines.append(f"- {ip_address}: {count}")
    else:
        lines.append("- No IP addresses found")

    lines.append("")
    lines.append("Important lines:")

    if analysis["important_lines"]:
        for item in analysis["important_lines"]:
            lines.append(f"- Line {item['line']}: {item['text']}")
    else:
        lines.append("- No important lines found")

    return "\n".join(lines)
