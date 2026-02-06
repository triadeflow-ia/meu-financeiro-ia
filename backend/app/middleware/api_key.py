"""
Middleware que exige o header X-API-KEY em todas as rotas /api/, exceto no webhook
(que usa validação própria com ZAPI_SECURITY_TOKEN).
"""
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.scope.get("path") or ""
        if not path.startswith("/api/"):
            return await call_next(request)

        # Webhook: não exige X-API-KEY aqui; a rota valida ZAPI_SECURITY_TOKEN
        if path.startswith("/api/webhook/"):
            return await call_next(request)

        api_key = (os.getenv("API_KEY") or "").strip()
        if not api_key:
            return await call_next(request)

        received = (request.headers.get("X-API-KEY") or "").strip()
        if received != api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Header X-API-KEY inválido ou ausente"},
            )
        return await call_next(request)
