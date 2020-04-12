from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'Hello'

class Todo(db.Model): # maybe can use more succinct naming conventions
    id = db.Column(db.Integer, primary_key=True) 
    code_name = db.Column(db.String(200), nullable=False)
    eq_type = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(200), nullable=False)
    prev_name = db.Column(db.String(200), default = '-')
    prev_email = db.Column(db.String(200), default = '-')
    name = db.Column(db.String(200), default = '-')
    email = db.Column(db.String(200), default = '-')
    prev_date_borrow = db.Column(db.String(200), default='-')
    date_borrow = db.Column(db.String(200), default='-')
    report = db.Column(db.String(200), default = '-')

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def home():
    error = None
    if request.method == 'POST':
        code = request.form['code']
        if code == 'admin':
            return render_template('login.html')
        else:
            item = Todo.query.filter_by(code_name=code).first()
            if item == None:
                error = 'No such item!'
                return render_template('home.html', error = error)
            elif code == 'Camus':
                camus = 'Exists'
                return render_template('form.html',item = item, camus = camus)
            return render_template('form.html',item = item)
    else:
        return render_template('home.html', error = error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != '12345':
            error = 'Wrong credentials!'
            return render_template('login.html', error = error)
        else:
            admin = request.form['username']
            session["admin"] = admin
            return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/index', methods=['POST', 'GET'])
def index():
    if "admin" in session:
        if request.method == 'POST':
            task_code_name = request.form['code_name']
            task_status = request.form['status']
            task_eq_type = request.form['eq_type']
            new_task = Todo(code_name = task_code_name, eq_type = task_eq_type , status=task_status)

            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect(url_for('index'))

            except:
                return 'There was an issue adding your task'

        else:
            tasks = Todo.query.order_by(Todo.id).all()
            return render_template('index.html', tasks=tasks)

    else:
        return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.code_name = request.form['code_name']
        task.status = request.form['status']
        task.eq_type = request.form['eq_type']
        task.report = request.form['report']
        try:
            db.session.commit()
            return redirect('/index')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)

@app.route('/form/<int:id>', methods=['GET', 'POST'])
def form(id):
    item = Todo.query.get_or_404(id)

    if request.method == 'POST':
        item.name = request.form['name']
        item.email = request.form['email']
        item.status = 'Borrowed'
        item.date_borrow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        check = 'form'

        try:
            db.session.commit()
            return render_template('display.html', item = item, check = check)
        except:
            return 'There was an issue updating your entry'

    else:
        return render_template('form.html', item = item)

@app.route('/rtn/<int:id>', methods=['GET', 'POST'])
def rtn(id):
    rtn = Todo.query.get_or_404(id)
    email = request.form['email2']
    if request.method == 'POST' and rtn.email == email:
        rtn.prev_name = rtn.name
        rtn.prev_email = rtn.email
        rtn.prev_date_borrow = rtn.date_borrow
        rtn.date_borrow = '-'
        rtn.status = 'Available'
        rtn.email = '-'
        rtn.name = '-'
        check = 'return'
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            db.session.commit()
            return render_template('display.html', item = rtn, check = check, time = time)
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('form.html', item = rtn)

@app.route('/display', methods=['GET', 'POST'])
def display():
    return render_template('display.html')

if __name__ == "__main__":
    app.run(debug=True)
