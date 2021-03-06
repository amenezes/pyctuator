import asyncio
import logging
import threading
import time

import requests
from aiohttp import web

from pyctuator.pyctuator import Pyctuator
from tests.conftest import PyctuatorServer


# mypy: ignore_errors
# pylint: disable=unused-variable
class AiohttpPyctuatorServer(PyctuatorServer):

    def __init__(self) -> None:
        self.app = web.Application()
        self.routes = web.RouteTableDef()

        self.pyctuator = Pyctuator(
            self.app,
            "AIOHTTP Pyctuator",
            "http://localhost:8888",
            "http://localhost:8888/pyctuator",
            "http://localhost:8001/register",
            registration_interval_sec=1,
        )

        @self.routes.get("/logfile_test_repeater")
        async def logfile_test_repeater(request: web.Request) -> web.Response:
            repeated_string = request.query.get("repeated_string")
            logging.error(repeated_string)
            return web.Response(text=repeated_string)

        @self.routes.get("/httptrace_test_url")
        async def get_httptrace_test_url(request: web.Request) -> web.Response:
            # Sleep if requested to sleep - used for asserting httptraces timing
            sleep_sec = request.query.get("sleep_sec")
            if sleep_sec:
                logging.info("Sleeping %s seconds before replying", sleep_sec)
                time.sleep(int(sleep_sec))

            # Echo 'User-Data' header as 'resp-data' - used for asserting headers are captured properly
            return web.Response(headers={"resp-data": str(request.headers.get("User-Data"))}, body="my content")

        self.app.add_routes(self.routes)

        self.thread = threading.Thread(target=self._start_in_thread)
        self.should_stop_server = False
        self.server_started = False

    async def _run_server(self) -> None:
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, "localhost", 8888)
        await site.start()
        self.server_started = True

        while not self.should_stop_server:
            await asyncio.sleep(1)

        await runner.shutdown()
        await runner.cleanup()

    def _start_in_thread(self) -> None:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._run_server())
        loop.stop()

    def start(self) -> None:
        self.thread.start()
        while not self.server_started:
            time.sleep(0.01)

    def stop(self) -> None:
        self.pyctuator.stop()
        self.should_stop_server = True
        self.thread.join()
