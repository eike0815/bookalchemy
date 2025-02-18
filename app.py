from flask import Flask, request, redirect, url_for, render_template, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
db.init_app(app)


@app.route('/')
def books():
    all_books = Book.query.all()
    all_authors = Author.query.all()
    return render_template('home.html', books=all_books)


@app.route('/add_author', methods = ['GET','POST'])
def add_author():
    """this function adds a new author to the db"""
    if request.method== 'POST':
        name  =request.form.get('name')
        birthdate_str = request.form.get('birthdate')
        date_of_death_str = request.form.get('date_of_death')
        if not name or not birthdate_str:
            print("name and date of birth are required")
        else:
            try:
                birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
                date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None
                new_author = Author(name=name, birthdate=birthdate, date_of_death =  date_of_death)
                db.session.add(new_author)
                db.session.commit()
                return redirect(url_for('books'))
            except ValueError:
                print("birth_date must be a valid date")
    return render_template('add_author.html')


@app.route('/add_book', methods = ['GET','POST'])
def add_book():
    """this function adds a book to the db"""
    if request.method== 'POST':
        title  =request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')
        if not title or not isbn or not author_id:
            print("title and isbn are required")
        else:
            try:
                author = Author.query.get(author_id)
                if not author:
                    print("Author not found")
                else:
                    new_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
                    db.session.add(new_book)
                    db.session.commit()
                    return redirect(url_for('books'))
            except ValueError:
                print("something mandatory is missing")
    return render_template('add_book.html')


@app.route('/books/sorted')
def get_sorted_books():
    """sorts the books in the db by title or author"""
    sort_by = request.args.get('sort', 'author').strip().lower()
    print(sort_by, "here")
    direction = request.args.get('direction', 'asc').strip().lower()
    order_by_column = Book.title
    if sort_by == 'author':
        order_by_column = Author.name
    if direction == 'desc':
        order_by_column = order_by_column.desc()
    sorted_books = (
        db.session.query(Book, Author)
        .join(Author, Book.author_id == Author.id)  # Explizites JOIN
        .order_by(order_by_column)
        .all()
    )
    resulttest = [{"book title": book[0].title, "authors name": book[1].name}
        for book in sorted_books]
    return jsonify(resulttest)


@app.route('/search')
def search_books():
    """this function searches the db for a book"""
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('home.html', books=[], search=True)
    books = Book.query.join(Author).filter(
        Book.title.ilike(f"%{query}%")
    ).all()

    return render_template('home.html', books=books, search=True)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """this function deletes a book from the db"""
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id  # save the authors id before the book is deleted
    db.session.delete(book)
    db.session.commit()
    # checking out if the author has also written different books in the db
    remaining_books = Book.query.filter_by(author_id=author_id).first()
    if not remaining_books:
        author = Author.query.get(author_id)
        if author:
            db.session.delete(author)
            db.session.commit()
    return redirect(url_for('books'))

"""
with app.app_context():
    print(f"Database engine: {db.engine}")
    db.create_all()
"""
if __name__=='__main__':
    app.run(debug=True)

