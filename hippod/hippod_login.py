import os
import datetime
from aiohttp import web
import logging


log = logging.getLogger()


# server error
ERROR = '''
<html>
   <head>
   <title>SERVER ERROR</title>
       <style type ="text/css">
              body { text-align:center; padding: 10%;
              font-weight: bold; font: 20px Helvetica, sans-serif; }
              a {padding: 30px;}
              h1 {color:#FF0000 ; font-family: Arial, Helvetica, sans-serif;
                  font-size: 30px;}
       </style>
   </head>
      <body>
          <h1> Sorry! Something went wrong </h1>
          <h2> Internal server error</h2>
          <p> Please visit us later</p>
          <p>The Team</p>
      </body>
</html>
'''


class Login:
    """ Hippod login

    Arguments:
        conf --> [configuration file]
        path --> [Path to templates]

    """

    def __init__(self, conf, path):
        self._conf = conf
        self._path = path
        if self._path.endswith('/'):
            self._path = self._path[:-1]
        self._login_html_file = self._path + '/login.html'
        self._redirect_html_file = self._path + '/redirect.html'
        self._index_html_file = self._path + '/index.html'

    def _check_the_file(self, filename):
        if not os.path.isfile(filename):
            log.warning("Internal server error\n"
                  "File not found:{}\r\n".format(filename))
            return False
        return True

    def _load_html_file(self, filename):
        if not self._check_the_file(filename):
            return False
        if not filename.endswith(".html"):
            log.error("Error: {} is not html file".format(filename))
            return False
        return open(filename).read()

    @property
    def get_cookie(self):
        """Return tuple of cookie name and value"""
        return self._cookie_name, self._cookie_value

    @get_cookie.setter
    def set_cookie(self, cookie):
        """ set cookie

        Default cookie:
            cookie name = 'OldTamil'
            cookie value = 0

        Set cookie allows you to cutomize cookie
        Arguments:
            cookie --> tuple of cookie name and value[int]

        Usage:
            set_cookie(cookie)
        """
        self._cookie_name, self._cookie_value = cookie
        if not isinstance(self._cookie_value, int):
            log.warning("Cookie value should be int. Failed to cutomize the cookie\n"
                  "Setting a default cookie")
            self._cookie_name = 'OldTamil'
            self._cookie_value = 0

    def _check_cookie(self, request):
        if not len(request.cookies) > 0:
            return False
        for requested_cookie_name, requested_cookie_value in request.cookies.items():
            if not (requested_cookie_name == self._cookie_name):
                return False
            try:
                if not int(requested_cookie_value) == self._cookie_value:
                    return False
                return True
            except ValueError:
                return False
            return False

    def check_configuration(self):
        if ('username' or 'password') not in self._conf.common:
            log.error("\nUser credentials are missing....\r\n")
            return False
        return True

    async def _check_credentials(self, username, password):
        authorized_username = self._conf.common.username
        authorized_password = self._conf.common.password
        if not (username == authorized_username and
                password == authorized_password):
            return False
        return True

    async def server_error(self, request):
        """server error"""
        return web.Response(text=ERROR, content_type='text/html')

    async def index(self, request):
        valid_cookie = self._check_cookie(request)
        if not valid_cookie:
            return web.HTTPFound('/log')
        index_html = self._load_html_file(self._index_html_file)
        if not index_html:
            return web.HTTPFound('/error')
        return web.Response(text=index_html, content_type='text/html')

    async def redirect_page(self, request):
        redirect_file = self._load_html_file(self._redirect_html_file)
        if not redirect_file:
            return web.HTTPFound('/error')
        valid_cookie = self._check_cookie(request)
        if not valid_cookie:
            return web.Response(text=redirect_file, content_type='text/html')
        return web.HTTPFound('/')

    async def login_page(self, request):
        login_file = self._load_html_file(self._login_html_file)
        if not login_file:
            return web.HTTPFound('/error')
        valid_cookie = self._check_cookie(request)
        if not valid_cookie:
            return web.Response(text=login_file, content_type='text/html')
        return web.HTTPFound('/')

    async def login_required(self, request):
        if not self.check_configuration():
            return web.HTTPFound('/error')
        form = await request.post()
        username = form.get('username')
        password = form.get('password')
        authorization = await self._check_credentials(username, password)
        if not authorization:
            return web.HTTPFound('/redirect')
        time_ = datetime.datetime.utcnow() + datetime.timedelta(
            days=30)
        cookie_expiry_date = time_.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = web.HTTPFound('/')
        response.set_cookie(self._cookie_name,
                            value=self._cookie_value,
                            expires=cookie_expiry_date)
        return response
