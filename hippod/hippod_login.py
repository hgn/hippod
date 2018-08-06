import os
import datetime
from aiohttp import web

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
    """ Hippod login """

    def __init__(self, conf, path):
        self._conf = conf
        self._path = path
        if self._path.endswith('/'):
            self._path = self._path[:-1]
        self._login_html_file = self._path + '/login.html'
        self._redirect_html_file = self._path + '/redirect.html'
        self._index_html_file = self._path + '/index.html'
        self._cookie_name = 'OldTamil'
        self._cookie_value = 1

    def _check_the_file(self, filename):
        if not os.path.isfile(filename):
            print("Internal server error\n"
                  "File not found:{}\r\n".format(filename))
            return False
        return True

    def _load_html_file(self, filename):
        if not self._check_the_file(filename):
            return False
        if not filename.endswith(".html"):
            print("{} is not html file".format(filename))
            return False
        return open(filename).read()

    def set_cookie(self, name, value):
        """ set cookie """
        self._cookie_name, self._cookie_value = name, value
        return None

    def _check_cookie(self, request):
        cookie_value = request.cookies.get(self._cookie_name, None)
        if not cookie_value:
            return False
        try:
            if not int(cookie_value) == self._cookie_value:
                return False
            return True
        except ValueError:
            return False
        return False

    def check_configuration(self):
        if ('username' or 'password') not in self._conf.common:
            print("\nWarning: User credentials are missing....\r\n")
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
