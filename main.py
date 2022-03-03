from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
import os

app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = os.environ["Secret-key"]

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///recetas.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# csrf = CSRFProtect(app)
# app.secret_key = os.environ["Password"]
PASSWORD = "nbicenice"


class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    ingredients = db.Column(db.String(550), nullable=False)
    instructions = db.Column(db.String(550), nullable=False)
    time = db.Column(db.Integer, nullable=False)
    time_sel = db.Column(db.String(10), nullable=False)


#db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    all_recetas = db.session.query(Receta).all()
    return render_template("index.html", recetas=all_recetas, busqueda_recetas=[])


@app.route("/add", methods=["GET", "POST"])
def add():
    all_recetas = db.session.query(Receta).all()
    types = [receta.type for receta in all_recetas]
    types = list(dict.fromkeys(types))

    if request.method == "POST":
        tipo = request.form["tipo"]
        nombre = request.form["nombre"]
        instrucciones = request.form["instrucciones"]
        ingredientes = request.form["ingredientes"]
        time = request.form["tiempo"]
        time_sel = request.form["time"]
        new_receta = Receta(type=tipo, title=nombre, ingredients=ingredientes,
                            instructions=instrucciones, time=time, time_sel=time_sel)
        db.session.add(new_receta)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add.html", types=types)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    receta_id = request.args.get("id")
    receta_selected = Receta.query.get(receta_id)

    all_recetas = db.session.query(Receta).all()
    types = [receta.type for receta in all_recetas]
    types = list(dict.fromkeys(types))

    if request.method == "POST":
        receta_id = request.form["id"]
        receta_to_update = Receta.query.get(receta_id)
        if len(request.form["tipo"]) > 0:
            receta_to_update.type = request.form["tipo"]
        if len(request.form["nombre"]) > 0:
            receta_to_update.title = request.form["nombre"]
        if len(request.form["ingredientes"]) > 0:
            receta_to_update.ingredients = request.form["ingredientes"]
        if len(request.form["instrucciones"]) > 0:
            receta_to_update.instructions = request.form["instrucciones"]
        if len(request.form["tiempo"]) > 0:
            receta_to_update.time = request.form["tiempo"]

        receta_to_update.time_sel = request.form["time"]

        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", receta=receta_selected, types=types)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    receta_id = request.args.get("id")
    receta_selected = Receta.query.get(receta_id)
    db.session.delete(receta_selected)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/search", methods=["GET", "POST"])
def search():
    all_recetas = db.session.query(Receta).all()
    search = request.args.get("search")
    search_type = request.args.get("search-type")
    recipes = None
    if str(search_type) == "type":
        recipes = Receta.query.filter_by(type=search).all()
    elif str(search_type) == "ingredients":
        recipes = Receta.query.filter(Receta.ingredients.ilike(f'%{search}%')).all()
    elif str(search_type) == "title":
        recipes = Receta.query.filter(Receta.title.ilike(f'%{search}%')).all()
    elif str(search_type) == "instructions":
        recipes = Receta.query.filter(Receta.instructions.ilike(f'%{search}%')).all()
    elif str(search_type) == "time":
        recipes = Receta.query.filter(Receta.time.ilike(f'%{search}%')).all()

    if recipes is None:
        return redirect("index.html")

    return render_template("index.html", recetas=all_recetas, busqueda_recetas=recipes)


if __name__ == '__main__':
    app.run(debug=True)
