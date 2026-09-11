from app.config import settings
from starlette.responses import JSONResponse


async def guard_browser_request(request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin not in settings.cors_origins_list:
            return JSONResponse({"detail": "Untrusted request origin"}, status_code=403)
    response = await call_next(request)
    if request.url.path.startswith("/api/v1/auth"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
    return response


guardBrowserRequest = guard_browser_request

__all__ = ["guardBrowserRequest", "guard_browser_request"]
