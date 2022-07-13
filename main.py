from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'todo_list_secret'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lists.db'
db = SQLAlchemy(app)


class ToDoList(db.Model):
    __tablename__ = 'to_do_lists'
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(50), unique=True, nullable=False)
    list_description = db.Column(db.String(500), nullable=False)
    list_items = relationship("ListItem", back_populates="parent_list", cascade='all, delete, delete-orphan')


class ListItem(db.Model):
    __tablename__ = 'all_list_items'
    id = db.Column(db.Integer, primary_key=True)
    list_item = db.Column(db.String(250), nullable=False)
    parent_list = relationship("ToDoList", back_populates="list_items")
    list_id = db.Column(db.Integer, db.ForeignKey("to_do_lists.id"), nullable=False)


# do only once at beginning
# db.create_all()


class ListForm(FlaskForm):
    name = StringField('List Name: ', validators=[DataRequired()])
    desc = StringField('Description: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ItemForm(FlaskForm):
    item = StringField('Add a new item: ', validators=[DataRequired()])
    submit = SubmitField('Add Item')


@app.route('/')
def lists():
    all_lists = db.session.query(ToDoList).all()
    return render_template('index.html', lists=all_lists)


@app.route('/list', methods=['GET', 'POST'])
def list():
    list_id = request.args.get('id')
    current_list = ToDoList.query.get(list_id)
    item_form = ItemForm()
    if item_form.validate_on_submit():
        new_item = ListItem(list_item=item_form.item.data, list_id=list_id)
        db.session.add(new_item)
        db.session.commit()
    return render_template('list.html', form=item_form, list=current_list, list_id=list_id)


@app.route('/add_list', methods=['GET', 'POST'])
def add_list():
    list_form = ListForm()
    if list_form.validate_on_submit():
        new_list = ToDoList(list_name=list_form.name.data, list_description=list_form.desc.data)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('lists'))
    return render_template('add.html', form=list_form)


@app.route('/edit_list', methods=['GET', 'POST'])
def edit_list():
    list_id = request.args.get('id')
    current_list = ToDoList.query.get(list_id)
    list_form = ListForm(name=current_list.list_name, desc=current_list.list_description)
    if list_form.validate_on_submit():
        current_list.list_name = list_form.name.data
        current_list.list_description = list_form.desc.data
        db.session.commit()
        return redirect(url_for('lists'))
    return render_template('add.html', form=list_form)


@app.route('/delete_list', methods=['GET', 'POST'])
def delete_list():
    list_id = request.args.get('id')
    current_list = ToDoList.query.get(list_id)
    db.session.delete(current_list)
    db.session.commit()
    return redirect(url_for('lists'))


@app.route('/delete_item', methods=['GET', 'POST'])
def delete_item():
    list_id = request.args.get('id')
    item_id = request.args.get('item_id')
    current_item = ListItem.query.get(item_id)
    db.session.delete(current_item)
    db.session.commit()
    return redirect(url_for('list', id=list_id))


if __name__ == '__main__':
    app.run(debug=True)
