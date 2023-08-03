from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import os 
from datetime import datetime

DB_NAME = 'notes.db'

app = Flask(__name__)

#app.config['SECRET_KEY']= "lkjhgfrtyuuop"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{DB_NAME}'
db = SQLAlchemy(app)
#class içinde tablo oluştururum sonra

class Users(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    surname = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(100), nullable = False)
    blogContents = db.relationship('Contents', backref='creator')

    def __repr__(self):
        return self.name + " " + self.surname

class Contents(db.Model):
    __tablename__="content"
    id=db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(200), nullable = False)
    blog_content = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route("/giris")
def giris():
    return render_template('giris.html')


@app.route("/")
def home():
    if 'email' in session:  # eger kullanıcı oturum açtıysa, oturumu açık tutmaya yarar
        email = session['email']
        me = Users.query.filter_by(email=email).first()
        contents = Contents.query.all()
        return render_template('home.html', me=me, contents=contents)
    return render_template('home.html')
    #return redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name=request.form.get('name')
        surname=request.form.get('surname')
        email=request.form.get('email')
        password=request.form.get('password')
       # if password=="": cant be empty


        #1 maille birden fazla hesap oluşturulmasını engllemek için
        search = Users.query.filter_by(email=email).first() # first ile ilk kaydolanı alır diğerine izin vermez

        if search != None:                        
            flash('Please enter another Email')
            return render_template('register.html')
        
        new_user =  Users(name=name, surname = surname, email = email, password = password)
        db.session.add(new_user)
        db.session.commit()
        flash('You were successfully logged in')
        return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route("/login", methods=["GET","POST"])
def login():
    if 'email' in session:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        search = Users.query.filter_by(email=email).first()

        if search is None:
            flash("Böyle bir hesap yoktur!")
            return render_template('login.html')
        if password == search.password:
            return redirect(url_for('home'))
        
    return render_template('login.html')


@app.route("/create",methods=["GET","POST"])
def create():
    
    if 'email' in session:
        email = session['email']
        me = Users.query.filter_by(email=email).first()
        if request.method=="POST":
            blog_title = request.form.get("blog_title")
            blog_content = request.form.get("blog_content")
            new_contents = Contents(blog_title = blog_title, blog_content = blog_content, creator_id = me.id)
            
            db.session.add(new_contents)
            db.session.commit()
            return redirect(url_for(''))
    return render_template('create.html')


@app.route("/detail")
def detail():
    return "hayal detayi"


@app.route("/logout")
def logout():
    session.pop("email",None)
    return redirect(url_for('homapage'))


@app.errorhandler(404)
def error(e):
    return render_template('404.html')

if __name__ == "__main__":
    
    if not os.path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
          
    app.debug = True
    app.run()