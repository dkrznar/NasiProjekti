from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

STATUSI = ["U pripremi", "Prijavljen", "U tijeku", "Završen", "Odbijen"]

class Projekt(db.Model):
    __tablename__ = "projekti"

    id = db.Column(db.Integer, primary_key = True)
    naziv = db.Column(db.String(200), nullable = False)
    naziv_poziva = db.Column(db.String(200))
    nadlezno_tijelo = db.Column(db.String(200))
    datum_pocetka = db.Column(db.Date)
    datum_zavrsetka = db.Column(db.Date)
    status = db.Column(db.String(20), default = "U pripremi")
    dobiveni_iznos = db.Column(db.Float, default = 0.0)
    nas_iznos = db.Column(db.Float, default = 0.0)
    klasa = db.Column(db.String(50))
    opis = db.Column(db.Text)
    datum_ugovora_financiranje = db.Column(db.Date)
    datum_ugovora_nabava = db.Column(db.Date)
    izvodac = db.Column(db.String(200))
    rok_izvrsenja = db.Column(db.Date)

    #pracenje unosa
    unio = db.Column(db.String(100))
    vrijeme_unosa = db.Column(db.DateTime, default = datetime.now)
    izmijenio = db.Column(db.String(100))
    vrijeme_izmjene = db.Column(db.DateTime)

    #Biljeske, prva je uvijek najnovija
    biljeske = db.relationship(
        "Biljeska",
        backref = "projekt",
        cascade = "all, delete-orphan",
        order_by = "Biljeska.vrijeme.desc()",
        lazy = True,
    )

    aneksi = db.relationship(
        "Aneks",
        backref="projekt",
        cascade="all, delete-orphan",
        order_by="Aneks.datum.desc()",
        lazy=True,
    )

    @property
    def ukupan_iznos(self):
        return round((self.dobiveni_iznos or 0) + (self.nas_iznos or 0), 2)
    

class Biljeska(db.Model):
    __tablename__ = "biljeske"

    id = db.Column(db.Integer, primary_key = True)
    projekt_id = db.Column(db.Integer, db.ForeignKey("projekti.id"), nullable = False)
    tekst = db.Column(db.Text, nullable = False)
    ime = db.Column(db.String(100))
    vrijeme = db.Column(db.DateTime, default = datetime.now)

class Aneks(db.Model):
    __tablename__ = "aneksi"

    id = db.Column(db.Integer, primary_key=True)
    projekt_id = db.Column(db.Integer, db.ForeignKey("projekti.id"), nullable=False)
    datum = db.Column(db.Date, nullable=False)
    napomena = db.Column(db.String(300))   # npr. "produljenje roka za 60 dana"
    dodao = db.Column(db.String(100))
