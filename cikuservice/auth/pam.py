import grp

from core.validation import Validation

class PamAuthMethod(AuthMethod):
    def __init__(self):
        try:
            from pam import pam
            self.pam = pam
        except ImportError:
            print("could not import 'pam'")
            sys.exit(1)

    
    def user_valid(self, valid: Validation, username: str, password: str) \
            -> bool:
        user = get_user(username)

        if user is None:

            valid_dummy = Validation({})

            if not valid_dummy.ok:
                valid.error('Username or password incorrect')
                return False

        else:

            username = user.username

        if not self.pam().authenticate(username, password, self.service):
            valid.error('Username or password incorrect')
            return False
