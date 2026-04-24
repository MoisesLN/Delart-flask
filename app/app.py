from flask import Flask, render_template
from db import db

app = Flask(__name__)
app.secret_key = 'd626428838bab4dd0736eb2e79918e0e'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db.init_app(app)


@app.route('/')
def cadastro():
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)