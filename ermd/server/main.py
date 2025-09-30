import uvicorn

def app() -> None:
    uvicorn.run(
        "ermd.server.server:app",
        host="127.0.0.1",
        port=4765,
        log_level="info",
        timeout_keep_alive=300,
    )
