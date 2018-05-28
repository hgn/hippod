# HippoD Login system

import os

import datetime

import json

from aiohttp import web


# Customize the cookie
# this is more convient way to modify cookie.
COOKIE_NAME = "OldTamil"
COOKIE_VALUE = 0


# Add required files.
LOGIN_HTML = 'templates/login.html'
SITE_HTML = 'templates/site.html'
REDIRECT_HTML = 'templates/redirect.html'
INDEX_FILE = 'templates/index.html'
CONFIG_FILE = 'assets/hippod-configuration.json'


# We use ERROR for server_error web response.
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
</html>'''


class Login:
    """ Login performs the main task of this system.

    The class runs login_required function which validate the user and gives
    permission and _check_the_file, _check_credentials, and _load_html_file
    are responsible for file handling and credentials loading.

    Cookie handling has been implemented.
    The cookie will be stored on the client site for 30 days long.


    """

    def _check_the_file(self, filename):
        if not os.path.isfile(filename):
            print("Internal server error! "
                  "file not found:{}".format(filename))
            return False
        return True

    def _load_html_file(self, filename):
        if not self._check_the_file(filename):
            return False
        if not filename.endswith(".html"):
            print("{} is not html file".format(filename))
            return False
        return open(filename).read()

    def _load_credentials(self, filename):
        """Load the user credentials from json file.

        First _load_credentials starts to read the json
        and make sure that the keys and values are accessible.

        Return to dictionary if the conditions succeed.
        """

        if not self._check_the_file(filename):
            return False
        if not filename.endswith(".json"):
            print("{} is not a json file.".format(filename))
            return False
        configure_file = open(filename)
        load_json_data = json.load(configure_file)
        if not load_json_data.get('common', {}).get('username'):
            return False
        return load_json_data

    # Return True if there is cookie with requested value.
    def _check_cookie(self, request):
        cookie_value = request.cookies.get(COOKIE_NAME, None)
        if not cookie_value:
            return False
        try:
            if not int(cookie_value) == COOKIE_VALUE:
                return False
            return True
        except ValueError:
            return False
        return False

    # Validating the user inputs with authorized credentials.
    def _check_credentials(self, username, password):
        credentials = self._load_credentials(CONFIG_FILE)
        if not credentials:
            return False
        authorized_username = credentials.get('common', {}).get('username')
        authorized_password = credentials.get('common', {}).get('password')
        if not (username == authorized_username and
                password == authorized_password):
            return False
        return True

    async def server_error(self, request):
        """Handles the server error.

        This function creates the server error web view.
        Simply Returns to a html web response.
        """
        return web.Response(text=ERROR, content_type='text/html')

    async def index(self, request):
        valid_cookie = self._check_cookie(request)
        if not valid_cookie:
            return web.HTTPFound('/log')
        home_file = self._load_html_file(INDEX_FILE)
        if not home_file:
            return web.HTTPFound('/error')
        return web.Response(text=home_file, content_type='text/html')

    async def redirect_page(self, request):
        redirect_file = self._load_html_file(REDIRECT_HTML)
        if not redirect_file:
            return web.HTTPFound('/error')
        valid_cookie = self._check_cookie(request)
        if not valid_cookie:
            return web.Response(text=redirect_file, content_type='text/html')
        return web.HTTPFound('/')

    async def login_page(self, request):
        login_file = self._load_html_file(LOGIN_HTML)
        if not login_file:
            return web.HTTPFound('/error')
        valid_cookie = self._check_cookie(request)
        if not valid_cookie:
            return web.Response(text=login_file, content_type='text/html')
        return web.HTTPFound('/')

    async def login_required(self, request):
        if not self._load_credentials(CONFIG_FILE):
            return web.HTTPFound('/error')
        form = await request.post()
        username = form.get('username')
        password = form.get('password')
        if not self._check_credentials(username, password):
            return web.HTTPFound('/redirect')
        # We are setting cookie on the client site after user successfully
        # logged in.
        time_ = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        cookie_expiry_date = time_.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = web.HTTPFound('/')
        response.set_cookie(COOKIE_NAME,
                            value=COOKIE_VALUE, expires=cookie_expiry_date)
        return response
