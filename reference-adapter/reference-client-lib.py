
class HippoDClientAdapter:

    def __init__(self):
        self.conf = {}
        self.find_username()

    def find_username_git_windows(self):
        return False, ""

    def find_username_git_unix(self):
        return False, ""

    def find_username_git(self):
        if os == win32:
            return find_username_git_windows()
        else
            return find_username_git_unix()

    def find_username():
        # first we try to get username from
        # global git configuration file
        success, username = find_username_git()
        if success:
            self.conf['username'] = username
            return
        raise Exception("cannot find a username - need one")

    def validate_configuration(self):
        if "username" not in self.conf:
            raise Exception("Did not found a username here - bad!")

    def execute(self, data):
        self.validate_configuration()
        self.validate_data(data)
        self.send_data(data)


if __name__ == '__main__':
    c = HippoDClientAdapter()
    c.set_hostname("hippod.local.net")
    c.set_port(8080)
    c.set_submitter(c.query_local_username())
