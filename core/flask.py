from core.config import get_origin, cfg
from flask import Flask, Response, request, url_for, render_template, redirect
from flask import Blueprint, current_app, g, abort, session as flask_session
from flask import make_response
from jinja2 import FileSystemLoader, ChoiceLoader, pass_context
from werkzeug.local import LocalProxy
from core.validation import Validation
import os
from functools import update_wrapper

class NamespacedSession:
    def __getitem__(self, key):
        return flask_session[f"{current_app.site}:{key}"]

    def __setitem__(self, key, value):
        flask_session[f"{current_app.site}:{key}"] = value

    def __delitem__(self, key):
        del flask_session[f"{current_app.site}:{key}"]

    def get(self, key, *args, **kwargs):
        return flask_session.get(f"{current_app.site}:{key}", *args, **kwargs)

    def set(self, key, *args, **kwargs):
        return flask_session.set(f"{current_app.site}:{key}", *args, **kwargs)
    
    def setdefault(self, key, *args, **kwargs):
        return flask_session.setdefault(
                f"{current_app.site}:{key}", *args, **kwargs)

    def pop(self, key, *args, **kwargs):
        return flask_session.pop(f"{current_app.site}:{key}", *args, **kwargs)

_session = NamespacedSession()
session = LocalProxy(lambda: _session)


class CikuFlask(Flask):
    def __init__(self, site, name,
            oauth_service=None, oauth_provider=None, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        self.site = site

        mod = __import__(name)
        if hasattr(mod, "__path__"):
            path = list(mod.__path__)[0]
        elif hasattr(mod, "__file__"):
            path = os.path.dirname(mod.__file__)
        else:
            raise Exception("Can't find the module's path, how are you running the app???")

        choices = [
                FileSystemLoader("templates"),
                FileSystemLoader(os.path.join("/etc", self.site, "templates")),
        ]

        self.mod_path = path
        choices.append(FileSystemLoader(os.path.join(path, "templates")))
        choices.append(FileSystemLoader(os.path.join(
            os.path.dirname(__file__),
            "templates"
        )))

        try:
            with open(os.path.join(path, "schema.graphqls")) as f:
                self.graphql_schema = f.read()
            with open(os.path.join(path, "default_query.graphql")) as f:
                self.graphql_query = f.read()
        except:
            pass

        self.jinja_env.globals['csrf_token'] = "csrf_token"
        self.jinja_env.add_extension('jinja2.ext.do')

        self.oauth_service = oauth_service
        self.oauth_provider = oauth_provider

        if self.oauth_service:
            from srht.oauth import oauth_blueprint
            self.register_blueprint(oauth_blueprint)

            from srht.oauth.scope import set_client_id
            set_client_id(self.oauth_service.client_id)

        # TODO: Remove
        self.no_csrf_prefixes = ['/api']

        @self.before_request
        def _csrf_check():
            if request.method != 'POST':
                return
            view = self.view_functions.get(request.endpoint)
            if not view:
                return
            view = "{0}.{1}".format(view.__module__, view.__name__)
            # TODO: Remove
            for prefix in self.no_csrf_prefixes:
                if request.path.startswith(prefix):
                    return
            token = flask_session.get('_csrf_token_v2', None)
            if not token:
                abort(403)
            if not secrets.compare_digest(token, request.form.get('_csrf_token')):
                abort(403)

        @self.errorhandler(401)
        def handle_401(e):
            if request.path.startswith("/api"):
                return { "errors": [ { "reason": "401 unauthorized" } ] }, 401
            return render_template("unauthorized.html"), 401

        @self.errorhandler(404)
        def handle_404(e):
            if request.path.startswith("/api"):
                return { "errors": [ { "reason": "404 not found" } ] }, 404
            return render_template("not_found.html"), 404

        @self.context_processor
        def inject():
            root = get_origin(self.site, external=True)
            ctx = {
                    'root': root,
                    'app': self,
                    'cfg': cfg,
                    'valid': Validation(request),
                    'environment': cfg("cikumeta", "environment", default="development")
            }
            return ctx
 




_csrf_bypass_views = set()
_csrf_bypass_blueprints = set()
        
def csrf_bypass(f):
    if isinstance(f, Blueprint):
        _csrf_bypass_blueprints.update([f])
    else:
        view = '.'.join((f.__module__, f.__name__))
        _csrf_bypass_views.update([view])
    return f


def cross_origin(f):
    """
    Enable CORS headers on a route.
    """

    f.required_methods = getattr(f, "required_methods", set())
    f.required_methods.add("OPTIONS")
    f.provide_automatic_options = False

    def wrapped_function(*args, **kwargs):
        if request.method == "OPTIONS":
            resp = current_app.make_default_options_response()
        else:
            resp = make_response(f(*args, **kwargs))
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "OPTIONS, GET, POST"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp

    return update_wrapper(wrapped_function, f)

        
