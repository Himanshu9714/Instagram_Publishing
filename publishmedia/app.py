from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from publish_content_all_users import *

app = Flask(__name__)
db = SQLAlchemy(app)


class InstagramUser(db.Model):
    username = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(400))

    def __str__(self) -> str:
        return f"<User: {self.username}>"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        content_publish_type = request.form["select"]
        return "WIP"
    return render_template("index.html")


@app.route("/login")
def login_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        client, response = login(username, password)
        if response:
            entry = InstagramUser(username=username, password=password)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
