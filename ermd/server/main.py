from argparse import ArgumentParser
import uvicorn

def app() -> None:
    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", default=4765, type=int, help="Port number")
    parser.add_argument("--log-level", default="info", type=str, help="Log level")
    parser.add_argument("--timeout-keep-alive", default=300, type=int, help="Timeout for keep-alive connections")
    parser.add_argument("--workers", default=None, type=int, help="Number of worker processes")
    parser.add_argument("--limit-concurrency", default=None, type=int, help="Number of threads per worker")
    parser.add_argument("--limit-max-requests", default=None, type=int, help="Maximum number of requests per worker")

    uvicorn.run("ermd.server.server:app", **vars(parser.parse_args()))
