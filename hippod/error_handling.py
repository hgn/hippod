from aiohttp import web

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
        message = " 404 Error! The page doesn't exit."
    return web.Response(text=message, content_type='text/html')



