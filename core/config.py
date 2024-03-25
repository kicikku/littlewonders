from glob import glob
from configparser import ConfigParser

class _Throw:
    pass

_config = None

def load_one(path):
    try:
        with open(path) as f:
            _config.read_file(f)
        return True
    except FileNotFoundError:
        return False

def load_config():
    global _config
    _config = ConfigParser()
    paths = ["config.ini", "/etc/kicikku/*.ini"]
    for path in paths:
        loaded = any(map(lambda p: load_one(p), glob(path)))
        if loaded:
            break

load_config()

def cfg(section, key, default=_Throw):
    if _config:
        if section in _config and key in _config[section]:
            return _config.get(section, key)
    if default == _Throw:
        raise Exception("Config option [{}] {} not found".format(section, key))
    return default

def get_origin(service, external=False, default=_Throw):
    if external:
        return cfg(service, "origin", default=default)
    return cfg(service, "internal-origin", default=
               cfg(service, "origin", default=default))
