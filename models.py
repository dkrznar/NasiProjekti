from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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

KATEGORIJE = ["Socijalna skrb", "Sport", "Obrazovanje i vrtići", "Kultura"]
STATUSI_ZAHTJEVA = ["Odobren", "Odbijen", "U obradi"]


class Stavka(db.Model):
    __tablename__ = "stavke"

    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(200), nullable=False)      # npr. "Jednokratne novčane pomoći"
    kategorija = db.Column(db.String(50), nullable=False)  # iz KATEGORIJE
    godina = db.Column(db.Integer, nullable=False)         # proračunska godina, npr. 2026
    opis = db.Column(db.Text)

    unio = db.Column(db.String(100))
    vrijeme_unosa = db.Column(db.DateTime, default=datetime.now)

    proracuni = db.relationship(
        "Proracun", backref="stavka",
        cascade="all, delete-orphan",
        order_by="Proracun.datum.desc(), Proracun.id.desc()",
        lazy=True,
    )
    zahtjevi = db.relationship(
        "Zahtjev", backref="stavka",
        cascade="all, delete-orphan",
        order_by="Zahtjev.datum.desc()",
        lazy=True,
    )

    @property
    def aktualni_proracun(self):
        # Najnoviji zapis proračuna (izvorni ili zadnji rebalans)
        if self.proracuni:
            return self.proracuni[0].iznos
        return 0.0

    @property
    def ukupno_isplaceno(self):
        # Zbrajaju se samo ODOBRENI zahtjevi
        return round(sum(z.iznos for z in self.zahtjevi if z.status == "Odobren"), 2)

    @property
    def preostalo(self):
        return round((self.aktualni_proracun or 0) - self.ukupno_isplaceno, 2)


class Proracun(db.Model):
    __tablename__ = "proracuni"

    id = db.Column(db.Integer, primary_key=True)
    stavka_id = db.Column(db.Integer, db.ForeignKey("stavke.id"), nullable=False)
    iznos = db.Column(db.Float, nullable=False)
    datum = db.Column(db.Date, nullable=False)
    napomena = db.Column(db.String(300))   # "izvorni proračun", "1. rebalans"...
    dodao = db.Column(db.String(100))


class Zahtjev(db.Model):
    __tablename__ = "zahtjevi"

    id = db.Column(db.Integer, primary_key=True)
    stavka_id = db.Column(db.Integer, db.ForeignKey("stavke.id"), nullable=False)
    datum = db.Column(db.Date, nullable=False)             # datum sjednice
    status = db.Column(db.String(20), default="Odobren")
    iznos = db.Column(db.Float, default=0.0)               # 0 kod odbijenih
    napomena = db.Column(db.String(300))
    unio = db.Column(db.String(100))

ULOGE = ["admin", "urednik", "pregled"]

class Korisnik(UserMixin, db.Model):
    __tablename__ = "korisnici"

    id = db.Column(db.Integer, primary_key=True)
    korisnicko_ime = db.Column(db.String(50), unique=True, nullable=False)
    ime_prezime = db.Column(db.String(100), nullable=False)
    lozinka_hash = db.Column(db.String(200), nullable=False)
    uloga = db.Column(db.String(20), default="urednik")
    aktivan = db.Column(db.Boolean, default=True)
    mora_promijeniti_lozinku = db.Column(db.Boolean, default=True)

    def postavi_lozinku(self, lozinka):
        self.lozinka_hash = generate_password_hash(lozinka)

    def provjeri_lozinku(self, lozinka):
        return check_password_hash(self.lozinka_hash, lozinka)

    @property
    def je_admin(self):
        return self.uloga == "admin"