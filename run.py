# run.py 

from flask import render_template
from flask_migrate import Migrate
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template("index.html") 


@app.route('/login')
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)

