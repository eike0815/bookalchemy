from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    date_of_death =db.Column(db.Date, nullable=True)
    books = db.relationship('Book', backref='autor')

    def __repr__(self):
        return f"authors name: {self.name}, born on {self.birthdate}."


class Book(db.Model):
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable= False, unique=True)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)


    def __repr__(self):
        return f"book title : {self.title}, published in  {self.publication_year}."






