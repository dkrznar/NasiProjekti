from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from models import db, Projekt, Biljeska, STATUSI

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///projekti.db"
app.config["SECRET_KEY"] = "zabok123"

db.init_app(app)

with app.app_context():
    db.create_all()

def parsiraj_datum(vrijednost):
    if vrijednost:
        return datetime.strptime(vrijednost, "%Y-%m-%d").date()
    return None

@app.route("/")
def index():
    projekti = Projekt.query.order_by(Projekt.datum_pocetka.desc()).all()
    return render_template("index.html", projekti=projekti)

@app.route("/projekt/novi", methods=["GET", "POST"])
def novi_projekt():
    if request.method == "POST":
        p = Projekt(
            naziv=request.form["naziv"].strip(),
            klasa=request.form.get("klasa", "").strip(),
            opis=request.form.get("opis", "").strip(),
            datum_pocetka=parsiraj_datum(request.form.get("datum_pocetka")),
            datum_zavrsetka=parsiraj_datum(request.form.get("datum_zavrsetka")),
            status=request.form.get("status", "U pripremi"),
            naziv_poziva=request.form.get("naziv_poziva", "").strip(),
            nadlezno_tijelo=request.form.get("nadlezno_tijelo", "").strip(),
            dobiveni_iznos=float(request.form.get("dobiveni_iznos") or 0),
            nas_iznos=float(request.form.get("nas_iznos") or 0),
            unio=request.cookies.get("korisnik"),
        )
        db.session.add(p)
        db.session.commit()
        flash("Projekt je spremljen.", "success")
        return redirect(url_for("index"))
 
    return render_template("form.html", statusi=STATUSI)
 
 
@app.route("/projekt/<int:projekt_id>")
def projekt_detalji(projekt_id):
    projekt = Projekt.query.get_or_404(projekt_id)
    return render_template("projekt_detalji.html", projekt=projekt)

@app.route("/projekt/<int:projekt_id>/biljeska", methods=["POST"])
def nova_biljeska(projekt_id):
    projekt = Projekt.query.get_or_404(projekt_id)
    b = Biljeska(
        projekt_id=projekt.id,
        tekst=request.form["tekst"].strip(),
        ime=request.cookies.get("korisnik"),
    )
    db.session.add(b)
    db.session.commit()
    flash("Bilješka je dodana.", "success")
    return redirect(url_for("projekt_detalji", projekt_id=projekt.id))

@app.route("/ime", methods=["GET", "POST"])
def postavi_ime():
    if request.method == "POST":
        ime = request.form["ime"].strip()
        odgovor = redirect(request.form.get("next") or url_for("index"))
        odgovor.set_cookie("korisnik", ime, max_age=60*60*24*365)
        return odgovor
    return render_template("ime.html", next=request.args.get("next", ""))

@app.before_request
def provjeri_ime():
    if request.endpoint in ("postavi_ime", "static"):
        return
    if not request.cookies.get("korisnik"):
        return redirect(url_for("postavi_ime", next=request.url))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port =5000)