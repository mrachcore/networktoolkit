import platform
import socket
import sys
from datetime import datetime

import psutil


def get_system_overview():
    """Collect basic local system information for the dashboard."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time

    return {
        "operating_system": f"{platform.system()} {platform.release()}",
        "hostname": socket.gethostname(),
        "local_ip": get_local_ip(),
        "uptime": format_uptime(uptime),
        "python_version": sys.version.split()[0],
    }


def get_local_ip():
    """Find the local IP address without sending real data to the internet."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
            test_socket.connect(("8.8.8.8", 80))
            return test_socket.getsockname()[0]
    except OSError:
        return "Unavailable"


def get_resource_usage():
    """Return CPU, memory, disk, and network usage information."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": memory.percent,
        "memory_used": bytes_to_gb(memory.used),
        "memory_total": bytes_to_gb(memory.total),
        "disk_percent": disk.percent,
        "disk_used": bytes_to_gb(disk.used),
        "disk_total": bytes_to_gb(disk.total),
        "bytes_sent": bytes_to_mb(network.bytes_sent),
        "bytes_received": bytes_to_mb(network.bytes_recv),
    }


def get_process_list(limit=15):
    """Return a small process list for display in a table."""
    processes = []

    for process in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            process_info = process.info
            processes.append(
                {
                    "PID": process_info["pid"],
                    "Process": process_info["name"] or "Unknown",
                    "CPU %": round(process_info["cpu_percent"] or 0, 1),
                    "Memory %": round(process_info["memory_percent"] or 0, 2),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Some system processes disappear or cannot be read. Skipping them is normal.
            continue

    processes.sort(key=lambda item: item["Memory %"], reverse=True)
    return processes[:limit]


def format_uptime(uptime):
    """Convert a timedelta into a readable uptime string."""
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m"

    return f"{hours}h {minutes}m"


def bytes_to_gb(value):
    return round(value / (1024 ** 3), 2)


def bytes_to_mb(value):
    return round(value / (1024 ** 2), 2)
