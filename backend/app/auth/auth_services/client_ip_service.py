# ---------------------------- External Imports ----------------------------
# FastAPI request object
from fastapi import Request

# ---------------------------- Client IP Utility ----------------------------
def get_client_ip(request: Request) -> str:
    """
    Extract the real client IP address from a FastAPI request.

    Order of priority:
    1. X-Forwarded-For header (first IP is the originating client)
    2. X-Real-IP header (set by some proxies)
    3. Fallback to request.client.host (direct connection)

    Args:
        request (Request): FastAPI request object

    Returns:
        str: The client IP address
    """
    # ---------------------------- Check X-Forwarded-For header ----------------------------
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # May contain multiple IPs if passing through proxies
        return x_forwarded_for.split(",")[0].strip()

    # ---------------------------- Check X-Real-IP header ----------------------------
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()

    # ---------------------------- Fallback to direct connection ----------------------------
    return request.client.host
