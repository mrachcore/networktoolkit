import ipaddress
import platform
import socket
import subprocess


def run_ping(host, count=4, timeout=15):
    """Run the local ping command and return the command output as text."""
    if not host:
        return "Please enter a host, domain, or IP address."

    system = platform.system().lower()

    # Windows uses -n for count. Linux and macOS use -c.
    if system == "windows":
        command = ["ping", "-n", str(count), host]
    else:
        command = ["ping", "-c", str(count), host]

    return _run_command(command, timeout=timeout)


def dns_lookup(domain):
    """Resolve a domain name to an IP address using Python's socket module."""
    if not domain:
        return {"success": False, "message": "Please enter a domain name."}

    try:
        ip_address = socket.gethostbyname(domain)
        return {"success": True, "domain": domain, "ip": ip_address}
    except socket.gaierror:
        return {"success": False, "message": f"Could not resolve '{domain}'."}


def run_traceroute(host, timeout=45):
    """Run traceroute/tracert depending on the operating system."""
    if not host:
        return "Please enter a host, domain, or IP address."

    system = platform.system().lower()

    # Windows ships with tracert. Linux/macOS usually use traceroute.
    if system == "windows":
        command = ["tracert", host]
    else:
        command = ["traceroute", host]

    return _run_command(command, timeout=timeout)


def calculate_subnet(cidr):
    """Calculate useful subnet information from CIDR notation."""
    if not cidr:
        return {"success": False, "message": "Please enter a CIDR network, for example 192.168.1.0/24."}

    try:
        # strict=False allows beginner-friendly input such as 192.168.1.55/24.
        network = ipaddress.ip_network(cidr, strict=False)
        result = {
            "success": True,
            "version": f"IPv{network.version}",
            "network_address": str(network.network_address),
            "netmask": str(network.netmask),
            "broadcast_address": str(network.broadcast_address) if network.version == 4 else "N/A for IPv6",
            "total_addresses": network.num_addresses,
            "usable_hosts": _usable_host_count(network),
            "first_host": "N/A",
            "last_host": "N/A",
        }

        first_host, last_host = _first_and_last_host(network)
        result["first_host"] = first_host
        result["last_host"] = last_host

        return result
    except ValueError as error:
        return {"success": False, "message": f"Invalid CIDR input: {error}"}


def check_tcp_port(host, port, timeout=3):
    """Check whether a TCP port is reachable."""
    if not host:
        return {"success": False, "open": False, "message": "Please enter a host."}

    try:
        port_number = int(port)
        if port_number < 1 or port_number > 65535:
            return {"success": False, "open": False, "message": "Port must be between 1 and 65535."}
    except (TypeError, ValueError):
        return {"success": False, "open": False, "message": "Port must be a number."}

    try:
        with socket.create_connection((host, port_number), timeout=timeout):
            return {
                "success": True,
                "open": True,
                "message": f"TCP port {port_number} on {host} is open.",
            }
    except (socket.timeout, ConnectionRefusedError, OSError):
        return {
            "success": True,
            "open": False,
            "message": f"TCP port {port_number} on {host} is closed or unreachable.",
        }


def _run_command(command, timeout):
    """Small helper for safe subprocess calls with timeout handling."""
    try:
        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = completed_process.stdout
        if completed_process.stderr:
            output += "\n" + completed_process.stderr

        return output.strip() or "Command finished without output."
    except FileNotFoundError:
        tool_name = command[0]
        return f"Command '{tool_name}' was not found on this system."
    except subprocess.TimeoutExpired:
        return "Command timed out. Try a different target or check your network connection."


def _usable_host_count(network):
    """Return a practical usable host count for IPv4 networks."""
    if network.version != 4:
        return "N/A for IPv6"

    if network.prefixlen >= 31:
        return 0

    return max(network.num_addresses - 2, 0)


def _first_and_last_host(network):
    """Calculate first and last host without creating a huge list in memory."""
    if network.num_addresses <= 2:
        hosts = list(network.hosts())
        if not hosts:
            return "N/A", "N/A"
        return str(hosts[0]), str(hosts[-1])

    first_host = network.network_address + 1
    last_host = network.broadcast_address - 1
    return str(first_host), str(last_host)
