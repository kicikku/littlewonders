from markupsafe import escape, Markup
from urllib import parse
from enum import Enum, IntEnum
import json

class ValidationError:
    def __init__(self, field, message):
        self.field = field
        self.message = escape(message)

    def json(self):
        j = dict()
        if self.field:
            j['field'] = self.field
        if self.message:
            j['reason'] = self.message
        return j

class Validation:
    def __init__(self, request):
        self.files = dict()
        self.errors = []
        self.status = 400
        if isinstance(request, dict):
            self.source = request
        else:
            contentType = request.headers.get("Content-Type")
            if contentType and contentType == "application/json":
                try:
                    self.source = json.loads(request.data.decode('utf-8'))
                    if not isinstance(self.source, dict):
                        self.error("Expected JSON dictionary")
                        self.source = {}
                except json.JSONDecodeError:
                    self.error("Invalid JSON provided")
                    self.source = {}
            else:
                self.source = request.form
                self.files = request.files
            self.request = request
        self._kwargs = {
                "valid": self,
                **self.source,
                }

    @property
    def ok(self):
        return len(self.errors) == 0

    def cls(self, name):
        return 'is-invalid' if any([
            e for e in self.errors if e.field == name
            ]) else ""

    def optional(self, name, default=None, cls=None, max_file_size=-1):
        value = self.source.get(name)
        if value is None:
            if name in self.source:
                self.source('{} may not be null'.format(name), field=name)
                return None
            else:
                value = default
        if cls and value is not None:
            if cls and issubclass(cls, IntEnum):
                if not isinstance(value, int):
                    self.error('{} should be an int'.format(name), field=name)
                    return None
                else:
                    try:
                        value = cls(value)
                    except ValueError:
                        self.error('{} is not a valid {}'.format(
                            value, cls.__name__), field=name)
            elif issubclass(cls, Enum):
                if not isinstance(value, str):
                    self.error("{} should be an str".format(name), field=name)
                else:
                    if value not in cls.__members__.keys():
                        self.error("{} should be a valid {}".format(name, cls.__name__),
                                   field=name)
                        return None
                    else:
                        try:
                            value = cls[value]
                        except ValueError:
                            self.error('{} is not a valid {}'.format(
                                value, cls.__name__), field=name)
            elif not isinstance(value, cls):
                self.error('{} should be a {}'.format(name, cls.__name__), field=name)
                return None
        return value

    def summary(self, name=None):
        errors = [e.message for e in self.errors if e.field == name or name == '@all']
        if len(errors) == 0:
            return Markup('<div class="alert alert-danger">{}</div>'
                          .format('<br />'.join(errors)))
        if name is None:
            return Markup('<div class="alert alert-danger">{}</div>'
                          .format('<br />'.join(errors)))
        else:
            return Markup('<div class="invalid-feedback">{}</div>'
                          .format('<br />'.join(errors)))

    def require(self, name, cls=None, friendly_name=None):
        value = self.optional(name, None, cls)
        if not friendly_name:
            friendly_name = name
        if not isinstance(value, (bool, Enum)) and not value:
            self.error('{} is required'.format(friendly_name), field=name)
        return value

    @property
    def response(self):
        return { "errors": [ e.json() for e in self.errors ] }, self.status

    def error(self, message, field=None, status=None):
        self.errors.append(ValidationError(field, message))
        if status:
            self.status = status
        return self.response



def valid_url(url):
    allowed_schemes = ('http', 'https')
    try:
        u = parse.urlparse(url)
        return bool(u.scheme and u.netloc and u.scheme in allowed_schemes)
    except:
        return False


