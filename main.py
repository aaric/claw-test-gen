"""Entry point for the todo application server."""

import uvicorn


def main(host: str = "127.0.0.1", port: int = 8000, reload: bool = True) -> None:
    """Start the Uvicorn server.

    Args:
        host: The host to bind to.
        port: The port to bind to.
        reload: Enable auto-reload on file changes.
    """
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
