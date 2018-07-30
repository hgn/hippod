from aiohttp import web
import os


class ErrorMiddleware:
    """ErrorMiddleware handles 404 error

    Arguments:
        filename --> Error html file

    Usage:
        error_middleware = ErrorMiddleware('404.html')
        app = web.Application(middlewares=[error_middleware.error_middleware])
    """

    def __init__(self, filename):
        self._filename = filename

    @web.middleware
    async def error_middleware(self, request, handler):
        try:
            response = await handler(request)
            if response.status != 404:
                return response
        except web.HTTPException as e:
            if e.status != 404:
                raise
        if not os.path.isfile(self._filename):
            return web.Response(text="404 Page not found",
                                content_type='text/html')
        ERROR_FILE = open(self._filename).read()
        return web.Response(text=ERROR_FILE, content_type='text/html')
