from flask import *
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = "lfjlkdf asfkjs fljasdf asdkfj sadlkf"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(30))
    password = db.Column(db.String(150))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50))
    email = db.Column(db.String(50))
    title = db.Column(db.String(50))
    content = db.Column(db.String(500))
    category = db.Column(db.String(50))
    city = db.Column(db.String(50))
    date = db.Column(db.DateTime)



@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
def home():
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template("home.html", posts=posts)

@app.route("/signup")
def signup():
	return render_template("signup.html")

@app.route("/login")
def login():
	return render_template("login.html")

@app.route("/insertUser",methods=["GET","POST"])
def insertUser():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        pswd = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("User Already Exists!!!","info")
        else:
            user = User(name=name, email=email, password=generate_password_hash(pswd))
            db.session.add(user)
            db.session.commit()
            flash("SignUp Successful!!!","info")
        return redirect("/signup")
    return "Error"

@app.route("/loginUser",methods=["GET","POST"])
def loginUser():
    if request.method == "POST":
        email = request.form.get("email")
        pswd = request.form.get("pwd")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, pswd):
                login_user(user)
                return redirect('/view')
            else:
                flash("Password Incorrect!!!","info")
                return redirect("/login")
        else:
            flash("User does not Exists!!!","info")
            return redirect("/login")
    return "Invalid"

@app.route("/addPost",methods=["GET","POST"])
def addPost():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category = request.form.get("category")
        city = request.form.get("city")
        post = Post(user=current_user.name, email=current_user.email, title=title, content=content, category=category, city=city, date=datetime.now())
        db.session.add(post)
        db.session.commit()
        flash("Post Successful","info")
        return redirect("/user")
    return "errror"

@app.route("/view")
@login_required
def view():
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template("userView.html", posts=posts)

@app.route("/user")
@login_required
def user():
    return render_template("user.html")

@app.route("/delete/<id>",methods=["POST","GET"])
@login_required
def delete(id):
    post = Post.query.filter_by(id=int(id)).first()
    print(post)
    db.session.delete(post)
    db.session.commit()
    return redirect("/userPosts")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/userPosts")
@login_required
def userPosts():
    email = current_user.email
    posts = Post.query.filter_by(email=email).order_by(Post.date.desc()).all()
    return render_template("posts.html",posts=posts)


if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)