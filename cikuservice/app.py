from flask import session
from core.flask import CikuFlask


class KicikkuAccountApp(CikuFlask):
    def __init__(self):
        super().__init__("meta.kicikku.com", __name__)

        from cikuservice.blueprints.auth import auth

        self.register_blueprint(auth)

app = KicikkuAccountApp()
