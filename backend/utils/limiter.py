from slowapi import Limiter
from slowapi.util import get_remote_address

# Seguridad A07: Configuración de Rate Limiting
limiter = Limiter(key_func=get_remote_address)
