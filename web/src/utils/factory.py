import calendar
import decimal
import uuid
from datetime import datetime, timedelta

from flask import Flask
from flask.json import JSONEncoder
from flask_cors import CORS


def create_app(package_name, config, blueprints=None, extensions=None):
    app = Flask(package_name)
    app.json_encoder = CustomJSONEncoder
    app.config.from_object(config)
    config.init_app(app)
    CORS(app)
    if blueprints:
        for bp in blueprints:
            app.register_blueprint(bp)
    if extensions:
        for extension in extensions:
            extension.init_app(app)

    return app


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                millis = int(
                    calendar.timegm(obj.timetuple()) * 1000 +
                    obj.microsecond / 1000
                )
                return millis
            if isinstance(obj, timedelta):
                return obj.total_seconds()
            iterable = iter(obj)
            if isinstance(obj, decimal.Decimal):
                # Convert decimal instances to strings.
                return float(obj)
            if isinstance(obj, uuid.UUID):
                return str(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
