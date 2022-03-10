from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mongoengine import MongoEngine
import os
from threading import Thread

db = MongoEngine()
app = Flask("Mis recetas", static_folder="static")

DB_URI = os.environ["MONGO_URI"]

app.config['MONGODB_SETTINGS'] = {
    "host": DB_URI,
    "connect": False
}

db.init_app(app)


class Receta(db.Document):
    type = db.StringField(required=True)
    title = db.StringField(required=True)
    ingredients = db.StringField(required=True)
    instructions = db.StringField(required=True)
    time = db.IntField(required=True)
    time_sel = db.StringField(required=True)


@app.route("/", methods=["GET", "POST"])
def home():
    all_recetas = Receta.objects.all()
    return render_template("index.html",
                           recetas=all_recetas,
                           busqueda_recetas=[])


@app.route("/add", methods=["GET", "POST"])
def add():
    all_recetas = Receta.objects.all()
    types = [receta.type for receta in all_recetas]
    types = list(dict.fromkeys(types))

    if request.method == "POST":
        tipo = request.form["tipo"]
        nombre = request.form["nombre"]
        instrucciones = request.form["instrucciones"]
        ingredientes = request.form["ingredientes"]
        time = request.form["tiempo"]
        time_sel = request.form["time"]
        new_receta = Receta(type=tipo,
                            title=nombre,
                            ingredients=ingredientes,
                            instructions=instrucciones,
                            time=time,
                            time_sel=time_sel)
        new_receta.save()
        return redirect(url_for("home"))

    return render_template("add.html", types=types)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        receta_id = request.form["id"]
        receta_to_update = Receta.objects(id=receta_id).first()

        receta_to_update.type = request.form["tipo"]
        receta_to_update.save()
        receta_to_update.update(set__title=request.form["nombre"])
        receta_to_update.update(set__ingredients=request.form["ingredientes"])
        receta_to_update.update(
            set__instructions=request.form["instrucciones"])
        receta_to_update.update(set__time=request.form["tiempo"])
        receta_to_update.update(set__time_sel=request.form["time"])

        return redirect(url_for('home'))

    receta_id = request.args.get("id")
    receta_to_update = Receta.objects(id=receta_id).first()

    all_recetas = Receta.objects.all()
    types = [receta.type for receta in all_recetas]
    types = list(dict.fromkeys(types))

    return render_template("edit.html", receta=receta_to_update, types=types)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    receta_id = request.args.get("id")
    receta_selected = Receta.objects(id=receta_id).first()
    db.Document.delete(receta_selected)
    return redirect(url_for('home'))


@app.route("/search", methods=["GET", "POST"])
def search():
    all_recetas = Receta.objects.all()
    search = request.args.get("search")
    search_type = request.args.get("search-type")
    recipes = None
    if str(search_type) == "type":
        recipes = Receta.objects(type__icontains=search).all()
    elif str(search_type) == "ingredients":
        recipes = Receta.objects(ingredients__icontains=search).all()
    elif str(search_type) == "title":
        recipes = Receta.objects(title__icontains=search).all()
    elif str(search_type) == "instructions":
        recipes = Receta.objects(instructions__icontains=search).all()
    elif str(search_type) == "time":
        recipes = Receta.objects(time__icontains=search).all()

    if recipes is None:
        return redirect("index.html")

    return render_template("index.html",
                           recetas=all_recetas,
                           busqueda_recetas=recipes)


def run():
    app.run(host='0.0.0.0', port=1234)


def keep_alive():
    t = Thread(target=run)
    t.start()
