import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Awaitable, Callable, Optional, cast

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from elysia.api.core.log import configure_logging, logger, set_log_level
from elysia.api.dependencies.common import get_user_manager
from elysia.api.middleware.error_handlers import register_error_handlers
from elysia.api.routes import (
    agents,
    collections,
    db,
    documents,
    feedback,
    init,
    processor,
    query,
    tools,
    tree_config,
    user_config,
    utils,
)
from elysia.api.utils.resources import print_resources

# Initialize logging early in the application lifecycle
configure_logging()

# Environment detection
IS_DEVELOPMENT = (
    os.getenv("NODE_ENV") == "development" or os.getenv("ENVIRONMENT") == "development"
)
NEXTJS_DEV_URL = os.getenv("NEXTJS_DEV_URL", "http://localhost:3000")

# Create HTTP client for proxying (only in development)
proxy_client: Optional[httpx.AsyncClient]
if IS_DEVELOPMENT:
    proxy_client = httpx.AsyncClient(timeout=30.0)
else:
    proxy_client = None


async def check_timeouts():
    user_manager = get_user_manager()
    await user_manager.check_all_trees_timeout()


async def output_resources():
    user_manager = get_user_manager()
    await print_resources(user_manager, save_to_file=True)


async def check_restart_clients():
    user_manager = get_user_manager()
    await user_manager.check_restart_clients()


@asynccontextmanager
async def lifespan(app: FastAPI):
    user_manager = get_user_manager()

    scheduler = AsyncIOScheduler()
    set_log_level("INFO")

    # use prime numbers for intervals so they don't overlap
    scheduler.add_job(check_timeouts, "interval", seconds=29)
    scheduler.add_job(check_restart_clients, "interval", seconds=31)
    scheduler.add_job(output_resources, "interval", seconds=1103)

    scheduler.start()
    yield
    scheduler.shutdown()

    await user_manager.close_all_clients()

    # Close proxy client if it exists
    if proxy_client:
        await proxy_client.aclose()

    # Attempt to cleanup litellm resources
    try:
        import litellm

        # Force cleanup of any async clients when the helper exists in the SDK
        close_clients = getattr(litellm, "close_litellm_async_clients", None)
        if callable(close_clients):
            close_fn = cast(Callable[[], Awaitable[None]], close_clients)
            await close_fn()
    except Exception:
        pass  # Ignore cleanup errors during shutdown


# Create FastAPI app instance
app = FastAPI(title="Elysia API", version="0.3.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
register_error_handlers(app)

# Include routers
app.include_router(init.router, prefix="/init", tags=["init"])
app.include_router(query.router, prefix="/ws", tags=["websockets"])
app.include_router(processor.router, prefix="/ws", tags=["websockets"])
app.include_router(collections.router, prefix="/collections", tags=["collections"])
app.include_router(user_config.router, prefix="/user/config", tags=["user config"])
app.include_router(tree_config.router, prefix="/tree/config", tags=["tree config"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(utils.router, prefix="/util", tags=["utilities"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])
app.include_router(db.router, prefix="/db", tags=["db"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])


# Health check endpoint (kept in main app.py due to its simplicity)
@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy"}


# Development proxy routes
if IS_DEVELOPMENT:
    logger.info(
        f"Running in development mode. Proxying frontend requests to {NEXTJS_DEV_URL}"
    )
    assert proxy_client is not None
    dev_proxy_client = proxy_client

    @app.api_route(
        "/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    )
    async def proxy_to_nextjs(request: Request, path: str):
        """Proxy requests to Next.js development server in development mode."""
        # Skip API routes - let them be handled by FastAPI
        if path.startswith("api/") or path.startswith("/api/"):
            # This should not happen as API routes are handled above, but just in case
            return {"error": "API route not found"}

        # Build the target URL
        target_url = f"{NEXTJS_DEV_URL}/{path}"
        if request.url.query:
            target_url += f"?{request.url.query}"

        try:
            # Forward the request to Next.js dev server
            body = await request.body()
            headers = dict(request.headers)
            # Remove host header to avoid issues
            headers.pop("host", None)

            response = await dev_proxy_client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=False,
            )

            # Return the response from Next.js
            return StreamingResponse(
                response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        except httpx.RequestError as e:
            logger.error(f"Proxy error: {e}")
            return {
                "error": "Frontend server not available. Make sure Next.js is running on port 3000."
            }

else:
    # Production: serve static files
    BASE_DIR = Path(__file__).resolve().parent

    # Serve NextJS _next assets at root level (this is crucial!)
    app.mount(
        "/_next",
        StaticFiles(directory=BASE_DIR / "static/_next"),
        name="next-assets",
    )

    # Serve other static files
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="app")

    @app.get("/")
    @app.head("/")
    async def serve_frontend():
        if os.path.exists(os.path.join(BASE_DIR, "static/index.html")):
            return FileResponse(os.path.join(BASE_DIR, "static/index.html"))
        else:
            return None
