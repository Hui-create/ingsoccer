from flask_script import Manager
from flask import Flask

from views import blue


app = Flask(__name__)

app.register_blueprint(blueprint=blue, url_prefix='/api')


if __name__ == '__main__':
    manage = Manager(app)
    manage.run()
