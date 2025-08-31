from flask_sqlalchemy import SQLAlchemy
# from todo import app
from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
from os.path import isfile
import importlib.resources as pkg_resources


import os

app = Flask(
        __name__,
        template_folder=str(pkg_resources.files("todolist") / "templates"),
        static_folder=str(pkg_resources.files("todolist") / "static")
    )

##### INITIALIZE DB ##########
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'todolist.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# db.app = app



class ToDo(db.Model):
    # Inherit the db.Model to this class.
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200),nullable=False)
    # completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return '<Task %r>' % self.id


if not isfile(db_path):
    with app.app_context():
        db.create_all()  # Create a db file is not already present


@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = ToDo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'DB update failed {e}'
    else:
        tasks = ToDo.query.order_by(ToDo.date_created).all()
        return render_template('index.html', tasks=tasks)

#### Update a task
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):

    task = ToDo.query.get_or_404(id) # get the task based on id

    if request.method == 'POST':
        task.content = request.form['content']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem updating the task'
    else:
        return render_template('update.html',task=task)


#### Delete a task
@app.route('/delete/<int:id>')
def delete(id):

    task_to_delete = ToDo.query.get_or_404(id) # get the task based on id

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting the task'

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()