"""A minimal logger: prints each line now and appends them all to a file on flush."""

import time

LOG_LINES: list[str] = []


def log(message: str) -> None:
    """Print a timestamped line and keep it for the next flush_log."""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Append the buffered lines to the log file and clear the buffer."""
    with open(path, "a", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in LOG_LINES)
    LOG_LINES.clear()
