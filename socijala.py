from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models import db, Stavka, Proracun, Zahtjev, STATUSI_ZAHTJEVA

socijala = Blueprint("socijala", __name__, url_prefix="/socijala")

KATEGORIJA = "Socijalna skrb"


@socijala.route("/")
def stavke():
    godina = request.args.get("godina", datetime.now().year, type=int)
    popis = (Stavka.query
             .filter_by(kategorija=KATEGORIJA, godina=godina)
             .order_by(Stavka.naziv.asc())
             .all())
    godine = [g[0] for g in db.session.query(Stavka.godina)
              .filter_by(kategorija=KATEGORIJA).distinct().order_by(Stavka.godina.desc())]
    return render_template("socijala_stavke.html", stavke=popis, godina=godina, godine=godine)


@socijala.route("/nova", methods=["POST"])
def nova_stavka():
    s = Stavka(
        naziv=request.form["naziv"].strip(),
        kategorija=KATEGORIJA,
        godina=int(request.form["godina"]),
        opis=request.form.get("opis", "").strip(),
        unio=request.cookies.get("korisnik"),
    )
    db.session.add(s)
    db.session.commit()
    flash("Stavka je dodana.", "success")
    return redirect(url_for("socijala.stavke", godina=s.godina))