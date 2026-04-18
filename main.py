import os
import sys
from werkzeug.middleware.proxy_fix import ProxyFix

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tele_crm.settings')

# Import the Django WSGI application
from tele_crm.wsgi import application

# Wrap the application with ProxyFix for Replit
# x_proto=1: Trust X-Forwarded-Proto
# x_host=1: Trust X-Forwarded-Host
# x_port=1: Trust X-Forwarded-Port
# x_prefix=1: Trust X-Forwarded-Prefix
app = ProxyFix(application, x_proto=1, x_host=1, x_port=1, x_prefix=1)

if __name__ == "__main__":
    import gunicorn.app.base

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.app = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.app

    port = int(os.environ.get("PORT", 3000))
    options = {
        'bind': '%s:%s' % ('0.0.0.0', port),
        'workers': 2,
        'accesslog': '-',
        'errorlog': '-',
    }
    StandaloneApplication(app, options).run()
