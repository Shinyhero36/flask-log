from flask import Flask
from flask_logger import FlaskLogger

app = Flask(__name__)
FlaskLogger(app)


@app.route("/")
def home():
    return """Hello World"""


@app.route("/test")
def test():
    return home()


if __name__ == "__main__":
    app.run(debug=True)