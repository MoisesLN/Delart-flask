from flask import Flask
from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)


@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)