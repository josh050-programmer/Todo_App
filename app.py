from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import render_template,request

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
#connexion a la database
db=SQLAlchemy(app)

class Task(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    #title=db.Column(db.String(255),nullable=False)
    content=db.Column(db.Text)
    status=db.Column(db.Boolean,default=False)

    def __init__(self,content):
        self.content=content
        #self.title=title
    
    def __repr(self):
        return '<Content %s>' % self.content
    
db.create_all()

@app.route('/')
def task_lists():
    tasks=Task.query.all()
    return render_template('list.html',tasks=tasks)

@app.route('/task',methods=['POST'])
def add_task():
    content=request.form['content']
    if not content:
        return 'Error'
    task=Task(content)
    db.session.add(task)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task=Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

@app.route('/done/<int:task_id>')
def resolve_task(task_id):
    task=Task.query.get(task_id)
    if not task:
        return redirect('/')
    if task.status:
        task.status=False
    else:
        task.status=True
    
    db.session.commit()
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)

    