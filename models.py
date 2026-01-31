from app import db

# -------------------------------
# Book model
# -------------------------------
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=True)

    quotes = db.relationship(
        'Quote',
        backref='book',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Book {self.id} | {self.title}>"


# -------------------------------
# Quote model
# -------------------------------
class Quote(db.Model):
    __tablename__ = 'quotes'

    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(
        db.Integer,
        db.ForeignKey('books.id'),
        nullable=False
    )

    text = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    type = db.Column(db.Integer, nullable=False)

    page = db.Column(db.Integer, nullable=True)
    location_start = db.Column(db.Integer, nullable=True)
    location_end = db.Column(db.Integer, nullable=True)

    is_active = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return (
            f"<Quote {self.id} | "
            f"Book={self.book_id} | "
            f"Loc={self.location_start}-{self.location_end}>"
        )


class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'

    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    location_start = db.Column(db.Integer, nullable=False)
    location_end = db.Column(db.Integer, nullable=False)

    text = db.Column(db.Text, nullable=False)
    translation = db.Column(db.Text)          # ✅ tradução da frase

    word = db.Column(db.Text)
    translated_word = db.Column(db.Text)      # ✅ tradução do termo

    notes = db.Column(db.Text)
    page = db.Column(db.Text)

    is_favorite = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Integer, default=1)

    status = db.Column(db.String)              # again / hard / good / easy

