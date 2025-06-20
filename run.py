# run.py 

from flask_migrate import Migrate
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

@app.route('/')
def hello():
    return "Hello JJulissa"

if __name__ == '__main__':
    app.run(debug=True)
