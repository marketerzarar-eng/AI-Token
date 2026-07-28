"""
Connectivity check used purely to gate the splash -> app transition.
Designed to fail *safe*: any exception is treated as "offline" rather
than crashing the application.
"""

import socket


def is_online(timeout: float = 2.5) -> bool:
    hosts = [
        ("1.1.1.1", 53),
        ("8.8.8.8", 53),
        ("dns.google", 443),
    ]
    for host, port in hosts:
        try:
            socket.setdefaulttimeout(timeout)
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except Exception:
            continue
    return False
