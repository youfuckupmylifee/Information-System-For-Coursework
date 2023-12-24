from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Настройки подключения к базе данных
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_store'

# Создание объекта подключения к MySQL
mysql = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/catalog')
def catalog():
    cursor = mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    return render_template('catalog.html', books=books)


@app.route('/book/<int:book_id>')
def book_details(book_id):
    cursor = mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id_book = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    return render_template('book_details.html', book=book)


@app.route('/order/<int:book_id>', methods=['GET', 'POST'])
def order_book(book_id):
    if request.method == 'POST':
        client_id = request.form['client_id']
        order_value = request.form['order_value']

        cursor = mysql.cursor()

        # Проверяем, есть ли клиент с таким ID
        cursor.execute("SELECT id_client FROM clients WHERE id_client = %s", (client_id,))
        result = cursor.fetchone()

        # Если клиента нет, то вы можете возвращать сообщение или редиректить на страницу создания клиента.
        if not result:
            cursor.close()
            return "Client not found. Please create a client first."

        # Если клиент найден, добавляем заказ
        cursor.execute("INSERT INTO orders (id_client, id_book, value, date) VALUES (%s, %s, %s, NOW())", (client_id, book_id, order_value))
        mysql.commit()
        cursor.close()

        return redirect(url_for('catalog'))

    return render_template('order_form.html', book_id=book_id)


@app.route('/create_client', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        client_name = request.form['client_name']
        client_phone = request.form['client_phone']

        cursor = mysql.cursor()
        cursor.execute("INSERT INTO clients (name, phone) VALUES (%s, %s)", (client_name, client_phone))  # Только одна вставка

        mysql.commit()
        cursor.close()

        return redirect(url_for('catalog'))

    return render_template('create_client.html')


@app.route('/delete_client/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    cursor = mysql.cursor()

    # Проверяем, есть ли заказы, связанные с этим клиентом
    cursor.execute("SELECT * FROM orders WHERE id_client = %s", (client_id,))
    if cursor.fetchone():
        return "Cannot delete client with active orders."

    # Удаление клиента
    cursor.execute("DELETE FROM clients WHERE id_client = %s", (client_id,))

    mysql.commit()
    cursor.close()

    return redirect(url_for('catalog'))


@app.route('/create_book', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        book_name = request.form['book_name']
        book_author = request.form['book_author']
        book_genre = request.form['book_genre']
        book_year = request.form['book_year']
        book_price = request.form['book_price']
        book_value = request.form['book_value']

        cursor = mysql.cursor()
        cursor.execute(
            "INSERT INTO books (name, author, genre, year, price, value) VALUES (%s, %s, %s, %s, %s, %s)",
            (book_name, book_author, book_genre, book_year, book_price, book_value)
        )
        mysql.commit()
        cursor.close()

        return redirect(url_for('catalog'))

    return render_template('create_book.html')


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if request.method == 'POST':
        book_name = request.form['book_name']
        book_author = request.form['book_author']
        book_genre = request.form['book_genre']
        book_year = request.form['book_year']
        book_price = request.form['book_price']
        book_value = request.form['book_value']

        cursor = mysql.cursor()
        cursor.execute(
            "UPDATE books SET name = %s, author = %s, genre = %s, year = %s, price = %s, value = %s WHERE id_book = %s",
            (book_name, book_author, book_genre, book_year, book_price, book_value, book_id)
        )
        mysql.commit()
        cursor.close()

        return redirect(url_for('catalog'))

    # Retrieve book details from the database based on the book_id
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM books WHERE id_book = %s", (book_id,))
    book_data = cursor.fetchone()
    cursor.close()

    if book_data:
        # Access the values using integer indices
        book_name = book_data[1]  # Index 1 corresponds to the 'name' column
        book_author = book_data[2]  # Index 2 corresponds to the 'author' column
        book_genre = book_data[3]  # Index 3 corresponds to the 'genre' column
        book_year = book_data[4]  # Index 4 corresponds to the 'year' column
        book_price = book_data[5]  # Index 5 corresponds to the 'price' column
        book_value = book_data[6]  # Index 6 corresponds to the 'value' column
    else:
        # Handle the case where the book is not found in the database
        # You can redirect or display an error message as needed.
        return "Book not found"

    return render_template('edit_book.html', book_id=book_id, book_name=book_name, book_author=book_author,
                           book_genre=book_genre, book_year=book_year, book_price=book_price,
                           book_value=book_value)


@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    cursor = mysql.cursor()

    # Проверяем, есть ли заказы, связанные с этой книгой
    cursor.execute("SELECT * FROM orders WHERE id_book = %s", (book_id,))
    if cursor.fetchone():
        return "Cannot delete book with active orders."

    # Удаление книги
    cursor.execute("DELETE FROM books WHERE id_book = %s", (book_id,))

    mysql.commit()
    cursor.close()

    return redirect(url_for('catalog'))


@app.route('/orders')
def orders_page():
    cursor = mysql.cursor(dictionary=True)  # dictionary=True позволит использовать имена столбцов для доступа к данным
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.close()
    return render_template('orders.html', orders=orders)


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    cursor = mysql.cursor()
    cursor.execute("DELETE FROM orders WHERE id_order = %s", (order_id,))
    mysql.commit()
    cursor.close()
    return redirect(url_for('orders_page'))


@app.route('/clients', endpoint='clients_page')
def clients():
    cursor = mysql.cursor(dictionary=True)  # dictionary=True позволит использовать имена столбцов для доступа к данным
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    cursor.close()
    return render_template('clients.html', clients=clients)


@app.route('/book_reviews')
def book_reviews():
    conn = mysql()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book_reviews")
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('book_reviews.html', reviews=reviews)


@app.route('/book_reviews/add', methods=('GET', 'POST'))
def add_review():
    if request.method == 'POST':
        id_book = request.form['id_book']
        id_client = request.form['id_client']
        rating = request.form['rating']
        comment = request.form['comment']

        conn = mysql()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO book_reviews (id_book, id_client, rating, comment, date) 
            VALUES (%s, %s, %s, %s, NOW())
            """, (id_book, id_client, rating, comment))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('book_reviews'))

    return render_template('add_review.html')


@app.route('/book_reviews/edit/<int:id_review>', methods=('GET', 'POST'))
def edit_review(id_review):
    conn = mysql()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        id_book = request.form['id_book']
        id_client = request.form['id_client']
        rating = request.form['rating']
        comment = request.form['comment']

        cursor.execute("""
            UPDATE book_reviews
            SET id_book=%s, id_client=%s, rating=%s, comment=%s
            WHERE id_review=%s
            """, (id_book, id_client, rating, comment, id_review))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('book_reviews'))

    # GET
    cursor.execute("SELECT * FROM book_reviews WHERE id_review=%s", (id_review,))
    review = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_review.html', review=review)


@app.route('/book_reviews/delete/<int:id_review>', methods=('POST',))
def delete_review(id_review):
    conn = mysql()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM book_reviews WHERE id_review=%s", (id_review,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('book_reviews'))




if __name__ == '__main__':
    app.run()
