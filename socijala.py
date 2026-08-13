from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models import db, Stavka, Proracun, Zahtjev, STATUSI_ZAHTJEVA
from pomocno import parsiraj_datum
from flask_login import current_user

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
        unio=current_user.ime_prezime,
    )
    db.session.add(s)
    db.session.commit()
    flash("Stavka je dodana.", "success")
    return redirect(url_for("socijala.stavke", godina=s.godina))

@socijala.route("/stavka/<int:stavka_id>")
def stavka_detalji(stavka_id):
    s = Stavka.query.get_or_404(stavka_id)
    return render_template("socijala_stavka.html", stavka=s, statusi=STATUSI_ZAHTJEVA)

@socijala.route("/stavka/<int:stavka_id>/zahtjev", methods=["POST"])
def novi_zahtjev(stavka_id):
    stavka = Stavka.query.get_or_404(stavka_id)
    z = Zahtjev(
        stavka_id=stavka_id,
        datum=parsiraj_datum(request.form.get("datum")),
        status=request.form.get("status", "Odobren"),
        iznos=float(request.form.get("iznos") or 0),
        napomena=request.form.get("napomena", "").strip(),
        unio=current_user.ime_prezime,
    )
    db.session.add(z)
    db.session.commit()
    flash("Zahtjev je dodan.", "success")
    return redirect(url_for("socijala.stavka_detalji", stavka_id=stavka_id))

@socijala.route("/stavka/<int:stavka_id>/proracun", methods=["POST"])
def novi_proracun(stavka_id):
    stavka = Stavka.query.get_or_404(stavka_id)
    pr = Proracun(
        stavka_id=stavka_id,
        iznos=float(request.form.get("iznos") or 0),
        datum=parsiraj_datum(request.form.get("datum")),
        napomena=request.form.get("napomena", "").strip(),
        dodao=current_user.ime_prezime,
    )
    db.session.add(pr)
    db.session.commit()
    flash("Proračun je ažuriran!", "success")
    return redirect(url_for("socijala.stavka_detalji", stavka_id=stavka_id))

@socijala.route("/zahtjev/<int:zahtjev_id>/obrisi", methods=["POST"])
def obrisi_zahtjev(zahtjev_id):
    z = Zahtjev.query.get_or_404(zahtjev_id)
    stavka_id = z.stavka_id      # ID stavke UZIMAMO iz pronađenog zahtjeva
    db.session.delete(z)
    db.session.commit()
    flash("Zahtjev je obrisan.", "warning")
    return redirect(url_for("socijala.stavka_detalji", stavka_id=stavka_id))

@socijala.route("/proracun/<int:proracun_id>/obrisi", methods=["POST"])
def obrisi_proracun(proracun_id):
    pr = Proracun.query.get_or_404(proracun_id)
    stavka_id = pr.stavka_id
    db.session.delete(pr)
    db.session.commit()
    flash("Proračun je obrisan.", "warning")
    return redirect(url_for("socijala.stavka_detalji", stavka_id=stavka_id))