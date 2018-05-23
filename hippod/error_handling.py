from aiohttp import web
from hippod import hippod_login



ERROR_FILE = open('templates/404.html').read()
@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status != 404:
            return response
        message = response.message
    except web.HTTPException as e:
        if e.status != 404:
            raise
    return web.Response(text=ERROR_FILE, content_type='text/html')



