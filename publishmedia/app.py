from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from publish_content_all_users import *
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev123455"
db = SQLAlchemy(app)

LOGIN = False
CLIENT = None


class InstagramUser(db.Model):
    username = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(400))

    def __str__(self) -> str:
        return f"<User: {self.username}>"


@app.route("/", methods=["GET", "POST"])
def index():

    # If user is not login with his/her IG username password, 
    # then he/she will be redirect to the login page
    if not LOGIN:
        return redirect(url_for("login_user"))

    if request.method == "POST":
        file = request.files["file"]
        content_publish_type = request.form["select"]
        
        if 'file' not in request.files:
            flash('No file part', category="danger")
            return redirect(request.url)

        if content_publish_type == "Carousel Object":
            image_files = []
            for file in request.files.getlist("file"):
                if file.filename == "":
                    continue
                file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_save_path)
                image_files.append(file_save_path)
            
            if image_files == []:
                flash("Please upload atleast one file to upload carousel object!", category="warning")
                return redirect(url_for("index.html"))

            message = upload_carousel_object(CLIENT, image_files, caption="Jay Shree Ram!")
            flash(message, category="success")
        
        elif content_publish_type != "":
            file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_save_path)

            if content_publish_type == "Image Post":
                message = upload_image_post(CLIENT, file_save_path, caption="Jay Shree Ram!")
                flash(message, category="success")

            elif content_publish_type == "Image Story":
                message = upload_photo_to_story(CLIENT, file_save_path, caption="Jay Shree Ram!")
                flash(message, category="success")

            elif content_publish_type == "Video Post":
                message = upload_video_post(CLIENT, file_save_path, caption="Jay Shree Ram!")
                flash(message, category="success")

            elif content_publish_type == "IGTV":
                message = upload_igtv(CLIENT, file_save_path, caption="Jay Shree Ram!")
                flash(message, category="success")
                
        
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        client, response = login(username, password)

        # response return from instagrapi login() module is boolean, it is set to global variable LOGIN
        # If LOGIN is true then & only then the user can access the index page.
        global LOGIN
        LOGIN = response
        if response:
            global CLIENT
            CLIENT = client
            try:
                # If Instagram login successfull, find the user user in database if exists 
                # and if he/she has changed the password then update the password with new one
                # and redirect to the index page
                user = InstagramUser.query.filter_by(username=username).first()
                if user.password != password:
                    user.password = password
                    db.session.commit()
                if user:
                    return redirect(url_for("index"))

            except Exception as e:
                logging.error(e)
            
            # Save the username and password of user to the database
            # TODO: Hash the password
            entry = InstagramUser(username=username, password=password)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
