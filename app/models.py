from db import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, nullable=False)
    senha = db.Column(db.String, nullable=False)

    agendamentos = db.relationship('Agendamento',backref='usuario') # backref -> cria o relacionamento inverso automaticamente

    def to_dict(self): #essa função serve para converter um objeto do SQLAlchemy em um dicionário Python comum, para depois o Flask conseguir transformar esse dicionário em JSON com jsonify().
        return {
            "id": self.id,
            "user": self.user
        }


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'

    id = db.Column(db.Integer, primary_key=True)
    agendamento_user = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=True
    )
    titulo = db.Column(db.String, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "agendamento_user": self.agendamento_user,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "status": self.status
        }