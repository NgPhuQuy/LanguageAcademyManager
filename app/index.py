from flask import render_template, request
from app import app
import dao

@app.route("/")
def index():
    pass

if __name__ == "__main__":
    app.run(debug=True)