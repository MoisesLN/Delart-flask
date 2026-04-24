from db import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.__str__)
    senha = db.Column(db.__str__)

class Agendamento(db.Model):
    __tablename__ = 'agendamento'

    id = db.Column(db.Integer, primary_key=True)
    agendamento_user = db.Column(db.__str__, db.ForeignKey('usuarios.id'))
    titulo = db.Column(db.__str__)
    descricao = db.Column(db.__str__)
    status = db.Column(db.Integer)