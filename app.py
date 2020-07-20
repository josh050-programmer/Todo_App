from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import render_template,request,url_for,redirect,session
import hashlib
from datetime import timedelta

app=Flask(__name__)
app.secret_key="hello"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['WTF_CSRF_ENABLED'] = True
app.permanent_session_lifetime=timedelta(minutes=5)

#connexion a la database
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(255),nullable=False)
    password=db.Column(db.String(255),nullable=False)
    task=db.relationship('Task',backref='user')

    def __init__(self,username,password):
        self.username=username
        self.password=hashlib.sha1(password.encode()).hexdigest()


class Task(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    content=db.Column(db.Text)
    status=db.Column(db.Boolean,default=False)
    id_creator=db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self,content,id_creator):
        self.content=content
        self.id_creator=id_creator
    

db.create_all()

@app.route('/login/',methods=['POST'])
def login():
    usernamed=request.form['username']
    password_entered=request.form['pwd']
    pwd=hashlib.sha1(password_entered.encode()).hexdigest()
    user = User.query.filter_by(username=usernamed,password=pwd).first()
    if user is None:
        error="Vos informations sont incorrectes...Réessayer"
        return render_template('index.html',error=error)
    else:
        session['id']=user.id
        session['username']=user.username
        return redirect(url_for('tasklist',id_c=user.id))


@app.route('/tasklist/<int:id_c>')
def tasklist(id_c):
    tasks=Task.query.filter_by(id_creator=id_c)
    return render_template('list.html',tasks=tasks)

@app.route('/add_task/',methods=['POST','GET'])
def add_task():
    content=request.form['content']
    if not content:
        return 'Error'
    task=Task(content,session['id'])
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('tasklist',id_c=session['id']))

@app.route('/delete_task/<int:task_id>',methods=['POST','GET'])
def delete_task(task_id):
    task=Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasklist',id_c=session['id']))

@app.route('/done_task/<int:task_id>',methods=['POST','GET'])
def done_task(task_id):
    task=Task.query.get(task_id)
    if not task:
          return redirect(url_for('tasklist',id_c=session['id']))
    if task.status:
        task.status=False
    else:
        task.status=True
    
    db.session.commit()
    return redirect(url_for('tasklist',id_c=session['id']))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user_add/')
def user_add():
    return render_template('add_user.html')


@app.route('/add_user/',methods=['POST'])
def add_user():
    user=request.form['pseudo']
    pwd=request.form['password']
    pwd_confirm=request.form['password_confirm']
    if pwd==pwd_confirm:
        if user.isprintable() and pwd.isprintable():
            user_=User(user,pwd)
            db.session.add(user_)
            db.session.commit()
            return render_template('index.html')
        else:
            var="Veuillez bien remplir le formulaire pour vous inscrire"
            return render_template('add_user.html',var=var)
    else:
        error="Vos mots de passe ne correspondent pas..Réessayer"
        return render_template('add_user.html',error=error)


@app.route('/logout')
def logout():
    session.pop('id',None)
    session.pop('username',None)
    return render_template('index.html')



if __name__=='__main__':
    app.run(debug=True)

    