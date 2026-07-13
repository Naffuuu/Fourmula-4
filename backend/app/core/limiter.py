from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by client IP. Applied per-route (see auth.py's /login) rather than
# globally, since public read endpoints and authenticated routes don't need
# the same aggressive throttling as the brute-force-prone login endpoint.
limiter = Limiter(key_func=get_remote_address)
