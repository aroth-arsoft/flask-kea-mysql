from flask import Blueprint, Flask, render_template
from flask import request, redirect
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect
from Model import Lease4
from Model import db
from forms import *
from tables import *

from resources.User import UserResource
from resources.Details import DetailsResource
from resources.TemplateRender import IndexResource, AddUser, AddDetails
from flask_cors import CORS

if 0:
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)

    template_bp = Blueprint('template', __name__)
    template = Api(template_bp)

    # Route
    template.add_resource(IndexResource, '/')
    template.add_resource(AddUser, 'addUser')
    template.add_resource(AddDetails, 'addDetails')
    api.add_resource(UserResource, '/User')
    api.add_resource(DetailsResource, '/Details')



def create_app(config_filename):
    app = Flask(__name__)
    CORS(app)
    csrf = CSRFProtect(app)

    app.config.from_object(config_filename)

    #from app import api_bp, template_bp
    #app.register_blueprint(api_bp, url_prefix='/api')
    #app.register_blueprint(template_bp, url_prefix='/')

    db.init_app(app)

    return app

#print('hello')
app = create_app("config")

@app.route("/",methods=['GET'])
def home():
    return redirect('/lease4')

@app.route("/lease4",methods=['POST', 'GET'])
def lease4():
    if request.method=='POST':
        title=request.form['title']
        description=request.form['description']
        todo=Todo(title=title ,description=description)
        db.session.add(todo)
        db.session.commit()
    items=Lease4.query.all()
    # Populate the table
    table = Lease4Table(items)

    return render_template('lease4.html',table=table)

@app.route("/lease4/add",methods=['POST', 'GET'])
def lease4_add():
    form = Lease4Form()
    if form.validate():
        return redirect('/lease4')
    return render_template('lease4_add.html', form=form)

@app.route("/lease4/edit",methods=['POST', 'GET'])
def lease4_edit():
    obj = Lease4()
    if request.method == "POST":
        form = Lease4Form(request.form, obj=obj)
        if form.validate():
            form.populate_obj(obj)
            db.session.add(obj)
            db.session.commit()
            return redirect('/lease4')
    else:
        address = request.args.get('address')
        obj = Lease4.query.filter_by(address=address).first()
        form = Lease4Form(obj=obj)
    return render_template('lease4_add.html', form=form)

if __name__ == "__main__":
    pass
    #app.run(host='0.0.0.0')