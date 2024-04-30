from flask_mysqldb import MySQL
import os
from user_validation.user_data_format import *
from user_validation.user_login_validator import *
from user_validation.user_register_validator import *
from datetime import datetime
from user_validation.rut_format import rut_format
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    jsonify,
    url_for,
    request,
    session,
)
from flask_session import Session
from pagination import Pagination
from functions import login_required, logged_in_redirect, admin_required
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Load environment variables from .env
load_dotenv()

# Configure Flask-MySQLdb
app.config["MYSQL_HOST"] = os.getenv("DB_HOST")
app.config["MYSQL_USER"] = os.getenv("DB_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("DB_PASS")
app.config["MYSQL_DB"] = os.getenv("DB_NAME")
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# Initialize MySQL
mysql = MySQL(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def database_user_register(cursor, rut, name, mail, password, permission="normal"):
    """
    Register a user into the database.

    This function registers a user into the database by inserting their RUT, name, email,
    permission level, and password into the appropriate database table. It uses the
    provided cursor to execute the SQL query for registration.

    Args:
        cursor: A database cursor object for executing SQL queries.
        rut (str): The user's RUT (Rol Único Tributario), a unique identification number.
        name (str): The user's name.
        mail (str): The user's email address.
        password (str): The user's password.
        permission (str, optional): The user's permission level (e.g., "normal" or "bibliotecario").
                                    Defaults to "normal" if not specified.

    Returns:
        None
    """

    cursor.execute(
        "INSERT INTO User (RUT, nombre, correo, permisos, contrasenia) VALUES (%s, %s, %s, %s, %s)",
        (
            rut,
            name,
            mail,
            permission,
            password,
        ),
    )
    mysql.connection.commit()


def search_books(template_name):
    # Retrieve query parameters for search, ordering, and pagination
    search_term = request.args.get("search", default="")
    order = request.args.get("o", default="id_book")
    direction = request.args.get("d", default="ASC").upper()
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Limit of items per page

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Start building the SQL query
    base_query = "SELECT * FROM Book"
    where_clause = ""
    order_clause = ""

    # Add a WHERE clause if a search term is provided
    if search_term:
        where_clause = " WHERE titulo LIKE %s"

    # Validate ordering parameters and add ORDER BY clause
    valid_columns = ["id_book", "titulo", "autor", "anio", "genero", "stock"]
    if order in valid_columns and direction in ["ASC", "DESC"]:
        order_clause = f" ORDER BY {order} {direction}"

    # Pagination clause
    pagination_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"

    # Complete SQL query for books
    query = f"{base_query}{where_clause}{order_clause}{pagination_clause}"

    # Execute the query with parameters if needed
    try:
        if search_term:
            cursor.execute(query, (f"%{search_term}%",))
        else:
            cursor.execute(query)
    except Exception as e:
        print("Error during query execution:", e)

    # Fetch the results
    books = cursor.fetchall()

    # Query for total count of books (for pagination)
    count_query = "SELECT COUNT(*) FROM Book" + where_clause
    cursor.execute(count_query, (f"%{search_term}%",) if search_term else ())
    result = cursor.fetchone()
    total_books = result["COUNT(*)"] if result else 0

    # Calculate total pages
    total_pages = (total_books + per_page - 1) // per_page

    cursor.close()

    # Check if the request is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"books": books, "total_pages": total_pages, "current_page": page}
        )

    # Create a Pagination object
    pagination = Pagination(page=page, per_page=per_page, total_count=total_books)

    # Render the template with the fetched books and pagination data
    return render_template(f"{template_name}.html", books=books, pagination=pagination)


# Route functions
@app.route("/")
@login_required
def index():
    """Show FuturaLib's homepage"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
@logged_in_redirect
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "GET":
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    else:
        # Get form data
        rut = request.form.get("rut")
        password = request.form.get("password")

        # Ensure both RUT and password were submitted
        errors = validate_login_input(rut, password)
        if errors:
            for error in errors:
                flash(error, "warning")
            return render_template("login.html")

        # Format RUT to delete spaces and hyphens
        rut = format_rut(request.form.get("rut"))

        # Create a new database cursor
        cursor = mysql.connection.cursor()

        # Query database for rut
        cursor.execute("SELECT * FROM User WHERE RUT = %s", (rut,))
        rows = cursor.fetchall()

        # Ensure rut exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["contrasenia"], request.form.get("password")
        ):
            flash("RUT y/o contraseña inválidos", "warning")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["RUT"]

        # Remember permission type of the user
        session["permission_type"] = rows[0]["permisos"]

        # Close the db cursor
        cursor.close()

        # Redirect user to home page
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
@logged_in_redirect
def register():
    """Register user"""
    if request.method == "GET":
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("register.html")
    else:
        # Get form data
        rut = request.form.get("rut")
        name = request.form.get("name")
        mail = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate user's entries
        errors = validate_register_input(rut, name, mail, password, confirmation)
        if errors:
            for error in errors:
                flash(error, "warning")
            return render_template("register.html")

        # Format RUT, mail and name
        formatted_rut, formatted_mail, formatted_name = format_data(rut, mail, name)

        # Check if rut is available
        cursor = mysql.connection.cursor()

        # Insert the user into the database
        try:
            cursor.execute("SELECT * FROM User WHERE RUT = %s", (formatted_rut,))
            rows = cursor.fetchall()
            if len(rows) > 0:
                flash("Error al registrarse: el usuario ya existe", "warning")
                return render_template("register.html")
        finally:
            cursor.close()

        # Insert the user into the users table
        try:
            cursor = mysql.connection.cursor()
            database_user_register(
                cursor,
                formatted_rut,
                formatted_name,
                formatted_mail,
                hash_password(password),
            )
        except Exception as e:
            # Handle the exception
            print("Error al intentar registrar el usuario:", e)
            flash("Error al registrar el usuario", "warning")
            return render_template("register.html")
        finally:
            cursor.close()

        flash("Usuario creado correctamente", "success")
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id and permissions
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quienes-somos", methods=["GET"])
def quienes_somos():
    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("quienes-somos.html")


@app.route("/biblioteca", methods=["GET"])
def biblioteca():
    return search_books("biblioteca")


@app.route("/agregar-libros", methods=["GET", "POST"])
@admin_required
def agregar_libro():
    if request.method == "GET":
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("agregar-libros.html")
    else:
        if not request.form.get("titulo"):
            flash(
                "Se debe introducir título.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-libros.html")
        elif not request.form.get("autor"):
            flash(
                "Se debe introducir autor.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-libros.html")
        elif not request.form.get("anio"):
            flash("Se debe introducir año.\nTodos los campos son obligarios", "warning")
            render_template("agregar-libros.html")
        elif not request.form.get("genero"):
            flash(
                "Se debe introducir género.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-libros.html")
        elif not request.form.get("stock"):
            flash(
                "Se debe introducir stock.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-libros.html")
        # User reached route via POST (as by submitting a form)
        titulo = request.form.get("titulo")
        autor = request.form.get("autor")
        anio = request.form.get("anio")
        genero = request.form.get("genero")
        stock = request.form.get("stock")
        print(titulo, autor, anio, genero, stock)

        cursor = mysql.connection.cursor()
        try:
            # Asegúrate de que los nombres de las columnas en la consulta coincidan con tu esquema de DB
            query = "INSERT INTO Book (titulo, autor, anio, genero, stock) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (titulo, autor, anio, genero, stock))
        except Exception as e:
            print("No se pudo registrar el libro:", e)
            flash("No se pudo registrar el libro.", "warning")
            return render_template("agregar-libros.html")

        mysql.connection.commit()
        cursor.close()

        # Flash book creation success
        flash(
            f"Libro creado correctamente.\nTítulo: {titulo}\nAutor: {autor}\nAño: {anio}\nGénero: {genero}\nStock: {stock}",
            "success",
        )
        return render_template("agregar-libros.html")


@app.route("/editar-libros", methods=["GET"])
@admin_required
def editar_libros():
    return search_books("editar-libros")


@app.route("/edit-book", methods=["GET", "POST"])
@admin_required
def edit_book():
    if request.method == "GET":
        # Get the book ID from the query parameter
        book_id = request.args.get("id")
        if not book_id:
            flash("No se proporcionó la ID del libro", "warning")
            return redirect(url_for("editar_libros"))

        # Connect to the database
        cursor = mysql.connection.cursor()

        # Retrieve the book's data
        try:
            cursor.execute(
                "SELECT id_book, titulo, autor, anio, genero, stock FROM Book WHERE id_book = %s",
                (book_id,),
            )
            book = cursor.fetchone()
        except Exception as e:
            print("No se pudieron obtener los datos del libro:", e)
            flash("No se pudieron obtener los datos del libro", "warning")
            return redirect(url_for("editar_libros"))

        cursor.close()

        # Check if the book exists
        if not book:
            flash("Libro no encontrado", "warning")
            return redirect(url_for("editar_libros"))

        # Render the edit-book.html template passing the book's data
        return render_template("edit-book.html", book=book)
    else:
        # POST request logic for updating book details
        try:
            # Retrieve the book ID and form data
            book_id = request.form.get("id_book")
            titulo = request.form.get("titulo")
            autor = request.form.get("autor")
            anio = request.form.get("anio")
            genero = request.form.get("genero")
            stock = request.form.get("stock")

            # Check if the book exists
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id_book FROM Book WHERE id_book = %s", (book_id,))
            if cursor.fetchone() is None:
                cursor.close()
                flash("Libro no encontrado", "warning")
                return redirect(url_for("editar_libros"))

            # Update the book's data
            update_query = """
                UPDATE Book
                SET titulo = %s, autor = %s, anio = %s, genero = %s, stock = %s
                WHERE id_book = %s
            """
            cursor.execute(update_query, (titulo, autor, anio, genero, stock, book_id))
            mysql.connection.commit()
            cursor.close()
            flash(f"Los datos del libro ID: {book_id} han sido actualizados", "success")
            return redirect(url_for("editar_libros"))

        except Exception as e1:
            print("Error al actualizar el libro:", e1)

            # Connect to the database
            cursor = mysql.connection.cursor()

            # Retrieve the book's data
            try:
                cursor.execute(
                    "SELECT id_book, titulo, autor, anio, genero, stock FROM Book WHERE id_book = %s",
                    (book_id,),
                )
                book = cursor.fetchone()
            except Exception as e2:
                print("No se pudieron obtener los datos del libro:", e2)
                return redirect(url_for("editar_libros"))

            cursor.close()
            flash("Error al actualizar el libro", "warning")
            return render_template("edit-book.html", book=book)


@app.route("/delete-book", methods=["GET"])
@admin_required
def delete_book():
    # Get the book ID from the query parameter
    book_id = request.args.get("id")
    if not book_id:
        flash("No se proporcionó la ID del libro", "warning")
        return redirect(url_for("editar_libros"))

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Delete the book by book id
    try:
        cursor.execute("DELETE FROM Solicitud WHERE id_book = %s", (book_id,))
        cursor.execute("DELETE FROM Lending WHERE id_book = %s", (book_id,))
        cursor.execute("DELETE FROM Book WHERE id_book = %s", (book_id,))
        mysql.connection.commit()
    except Exception as e:
        print("No se pudo eliminar el libro:", e)
        flash("No se pudo eliminar el libro", "warning")
        return render_template("editar-libros.html")
    cursor.close()

    flash(f"Se eliminó el libro ID: {book_id}", "success")
    return redirect(url_for("editar_libros"))


@app.route("/agregar-usuarios", methods=["GET", "POST"])
@admin_required
def agregar_usuarios():
    if request.method == "GET":
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("agregar-usuarios.html")
    else:
        # Get form data
        rut = request.form.get("rut")
        name = request.form.get("name")
        mail = request.form.get("mail")
        permission = request.form.get("permisos")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate user's entries
        errors = validate_register_input(
            rut, name, mail, password, confirmation, permission
        )
        if errors:
            for error in errors:
                flash(error, "warning")
            return render_template("agregar-usuarios.html")

        # Format RUT, mail and name
        formatted_rut, formatted_mail, formatted_name = format_data(rut, mail, name)

        # Check if rut is available
        cursor = mysql.connection.cursor()

        # Insert the user into the database
        try:
            cursor.execute("SELECT * FROM User WHERE RUT = %s", (formatted_rut,))
            rows = cursor.fetchall()
            if len(rows) > 0:
                flash("Error al registrar: el usuario ya existe", "warning")
                return render_template("agregar-usuarios.html")
        finally:
            cursor.close()

        # Insert the user into the users table
        try:
            cursor = mysql.connection.cursor()
            database_user_register(
                cursor,
                formatted_rut,
                formatted_name,
                formatted_mail,
                hash_password(password),
                permission,
            )
            mysql.connection.commit()
        except Exception as e:
            # Handle the exception
            print("Error al intentar registrar el usuario:", e)
            flash("Error al registrar el usuario", "warning")
            return render_template("agregar-usuarios.html")
        finally:
            cursor.close()

        flash(
            f"Usuario creado correctamente.\nRUT: {rut}\nNombre: {name}\nCorreo: {mail}\nPermisos: {permission}\nContraseña: {password}",
            "success",
        )
        return render_template("agregar-usuarios.html")


@app.route("/editar-usuarios", methods=["GET"])
@admin_required
def editar_usuarios():
    # Retrieve query parameters for search, ordering, and pagination
    search_term = request.args.get("search", default="")
    order = request.args.get("o", default="nombre")
    direction = request.args.get("d", default="ASC").upper()
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Limit of items per page

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Start building the SQL query
    base_query = "SELECT RUT, nombre, correo, permisos FROM User"
    where_clause = ""
    order_clause = ""

    # Add a WHERE clause if a search term is provided
    if search_term:
        where_clause = " WHERE nombre LIKE %s OR correo LIKE %s"

    # Validate ordering parameters and add ORDER BY clause
    valid_columns = ["rut", "nombre", "correo", "permisos"]
    if order in valid_columns and direction in ["ASC", "DESC"]:
        order_clause = f" ORDER BY {order} {direction}"

    # Pagination clause
    pagination_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"

    # Complete SQL query for users
    query = f"{base_query}{where_clause}{order_clause}{pagination_clause}"

    # Execute the query with parameters if needed
    try:
        if search_term:
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute(query)
    except Exception as e:
        print("Error during query execution:", e)

    # Fetch the results
    users = cursor.fetchall()

    # Query for total count of users (for pagination)
    count_query = "SELECT COUNT(*) FROM User" + where_clause
    cursor.execute(
        count_query, (f"%{search_term}%", f"%{search_term}%") if search_term else ()
    )
    result = cursor.fetchone()
    total_users = result["COUNT(*)"] if result else 0

    # Calculate total pages
    total_pages = (total_users + per_page - 1) // per_page

    cursor.close()

    # Check if the request is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"users": users, "total_pages": total_pages, "current_page": page}
        )

    # Create a Pagination object
    pagination = Pagination(page=page, per_page=per_page, total_count=total_users)

    # Render the template with fetched users and pagination data
    return render_template("editar-usuarios.html", users=users, pagination=pagination)


@app.route("/edit-user", methods=["GET", "POST"])
@admin_required
def edit_user():
    if request.method == "GET":
        # Get the RUT from the query parameter
        user_rut = request.args.get("id")
        if not user_rut:
            flash("No se proporcionó el RUT", "warning")
            return redirect(url_for("editar_usuarios"))

        # Connect to the database
        cursor = mysql.connection.cursor()

        # Retrieve the user's data
        try:
            cursor.execute(
                "SELECT RUT, nombre, correo, permisos FROM User WHERE RUT = %s",
                (user_rut,),
            )
            user = cursor.fetchone()
        except Exception as e:
            print("No se pudieron obtener los datos del usuario:", e)
            flash("No se pudieron obtener los datos del usuario", "warning")
            return redirect(url_for("editar_usuarios"))

        cursor.close()

        # Check if the user exists
        if not user:
            flash("Usuario no encontrado", "warning")
            return redirect(url_for("editar_usuarios"))

        # Render the edit-user.html template passing the user's data
        return render_template("edit-user.html", user=user)
    else:
        # POST request logic for updating user details
        try:
            # Retrieve the RUT and form data
            formatted_rut = request.form.get("hidden_formatted_rut")
            user_rut = request.form.get("rut")
            nombre = request.form.get("nombre")
            correo = request.form.get("correo")
            permisos = request.form.get("permisos")

            # Check if mail's format is correct
            if not is_email_complex(correo):
                flash(
                    "El correo debe estar en un formato correcto. Ejemplo: 'example@example.com'",
                    "warning",
                )
                raise Exception("El correo no tiene un formato adecuado.")

            # Check if the user exists
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT RUT FROM User WHERE RUT = %s", (user_rut,))
            if cursor.fetchone() is None:
                cursor.close()
                flash("Usuario no encontrado", "warning")
                return redirect(url_for("editar_usuarios"))

            # Update the user's data
            update_query = """
                UPDATE User
                SET nombre = %s, correo = %s, permisos = %s
                WHERE RUT = %s
            """
            cursor.execute(update_query, (nombre, correo, permisos, user_rut))
            mysql.connection.commit()
            cursor.close()
            flash(
                f"Los datos del usuario RUT: {formatted_rut} han sido actualizados",
                "success",
            )
            return redirect(url_for("editar_usuarios"))

        except Exception as e1:
            print("Error al actualizar el usuario:", e1)

            # Connect to the database
            cursor = mysql.connection.cursor()

            # Retrieve the user's data
            try:
                cursor.execute(
                    "SELECT RUT, nombre, correo, permisos FROM User WHERE RUT = %s",
                    (user_rut,),
                )
                user = cursor.fetchone()
            except Exception as e2:
                print("No se pudieron obtener los datos del usuario:", e2)
                return redirect(url_for("editar_usuarios"))

            cursor.close()
            flash("Error al actualizar el usuario", "warning")
            return render_template("edit-user.html", user=user)


@app.route("/delete-user", methods=["GET"])
@admin_required
def delete_user():
    # Get the RUT from the query parameter
    user_rut = request.args.get("id")
    if not user_rut:
        flash("No se proporcionó el RUT", "warning")
        return redirect(url_for("editar_usuarios"))

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Delete the user by RUT
    try:
        cursor.execute("DELETE FROM Solicitud WHERE RUT_User = %s", (user_rut,))
        cursor.execute("DELETE FROM Lending WHERE RUT_User = %s", (user_rut,))
        cursor.execute("DELETE FROM User WHERE RUT = %s", (user_rut,))
        mysql.connection.commit()
    except Exception as e:
        print("No se pudo eliminar el usuario:", e)
        flash("No se pudo eliminar el usuario", "warning")
        return render_template("editar-usuarios.html")
    cursor.close()

    flash(f"Se eliminó el usuario RUT: {rut_format(user_rut)}", "success")
    return redirect(url_for("editar_usuarios"))


@app.route("/ver-prestamos", methods=["GET"])
@admin_required
def ver_prestamos():
    # Retrieve query parameters for search, ordering, and pagination
    search_term = request.args.get("search", default="")
    order = request.args.get("o", default="order_id")
    direction = request.args.get("d", default="ASC").upper()
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Limit of items per page

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Start building the SQL query
    base_query = """
    SELECT 
        L.order_id, 
        L.RUT_User, 
        L.id_book, 
        B.titulo,
        L.fecha_entrega, 
        L.fecha_devolucion, 
        L.estado 
    FROM 
        Lending L
    JOIN 
        Book B ON L.id_book = B.id_book
"""

    where_clause = ""
    order_clause = ""

    # Add a WHERE clause if a search term is provided
    if search_term:
        where_clause = """
            WHERE 
                L.order_id LIKE %s 
                OR L.RUT_User LIKE %s 
                OR L.id_book LIKE %s
                OR B.titulo LIKE %s
                OR L.fecha_entrega LIKE %s 
                OR L.fecha_devolucion LIKE %s 
                OR L.estado LIKE %s
        """

    # Validate ordering parameters and add ORDER BY clause
    valid_columns = [
        "L.order_id",
        "L.RUT_User",
        "L.id_book",
        "B.titulo",
        "L.fecha_entrega",
        "L.fecha_devolucion",
        "L.estado",
    ]
    if order in valid_columns and direction in ["ASC", "DESC"]:
        order_clause = f" ORDER BY {order} {direction}"

    # Pagination clause
    pagination_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"

    # Complete SQL query for loans
    query = f"{base_query}{where_clause}{order_clause}{pagination_clause}"

    # Execute the query with parameters if needed
    try:
        if search_term:
            cursor.execute(
                query,
                (
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                ),
            )
        else:
            cursor.execute(query)
    except Exception as e:
        print("Error during query execution:", e)

    # Fetch the results
    loans = cursor.fetchall()

    # Format dates
    for loan in loans:
        loan["fecha_entrega"] = loan["fecha_entrega"].strftime("%d-%m-%Y")
        if loan["fecha_devolucion"]:
            loan["fecha_devolucion"] = loan["fecha_devolucion"].strftime("%d-%m-%Y")
    
    # Query for total count of loans (for pagination)
    count_query = "SELECT COUNT(*) FROM Lending" + where_clause
    cursor.execute(
        count_query,
        (
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
        )
        if search_term
        else (),
    )
    result = cursor.fetchone()
    total_loans = result["COUNT(*)"] if result else 0

    # Calculate total pages
    total_pages = (total_loans + per_page - 1) // per_page

    cursor.close()

    # Check if the request is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"loans": loans, "total_pages": total_pages, "current_page": page}
        )

    # Create a Pagination object
    pagination = Pagination(page=page, per_page=per_page, total_count=total_loans)

    # Render the template with fetched loans and pagination data
    return render_template("ver-prestamos.html", loans=loans, pagination=pagination)


@app.route("/edit-loan", methods=["GET", "POST"])
@admin_required
def edit_loan():
    if request.method == "GET":
        # Get the loan ID from the query parameter
        loan_id = request.args.get("id")
        if not loan_id:
            flash("No se proporcionó la ID del préstamo", "warning")
            return redirect(url_for("ver_prestamos"))

        # Connect to the database
        cursor = mysql.connection.cursor()

        # Retrieve the loan's data
        try:
            cursor.execute(
                """
                SELECT 
                    L.order_id,
                    L.fecha_entrega, 
                    L.fecha_devolucion, 
                    L.estado,
                    B.titulo
                FROM 
                    Lending L
                JOIN 
                    Book B ON L.id_book = B.id_book
                WHERE 
                    L.order_id = %s
                """,
                (loan_id,),
            )
            loan = cursor.fetchone()
        except Exception as e:
            print("No se pudieron obtener los datos del prestamo:", e)
            flash("No se pudieron obtener los datos del prestamo", "warning")
            return redirect(url_for("ver_prestamos"))

        cursor.close()

        # Check if the loan exists
        if not loan:
            flash("Préstamo no encontrado", "warning")
            return redirect(url_for("ver_prestamos"))

        # Render the edit-loan.html template passing the loan's data
        return render_template("edit-loan.html", loan=loan)
    else:
        # POST request logic for updating loan details
        try:
            # Retrieve the loan ID and form data
            loan_id = request.form.get("order_id")
            fecha_entrega = request.form.get("fecha_entrega")
            fecha_devolucion = request.form.get("fecha_devolucion")
            estado = request.form.get("estado")
            
            print(loan_id)

            # Check if the loan exists
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT order_id FROM Lending WHERE order_id = %s", (loan_id,))
            if cursor.fetchone() is None:
                cursor.close()
                flash("Préstamo no encontrado", "warning")
                return redirect(url_for("ver_prestamos"))

            # Update the loan's data
            update_query = """
                UPDATE Lending
                SET fecha_entrega = %s, fecha_devolucion = %s, estado = %s
                WHERE order_id = %s
            """
            cursor.execute(update_query, (fecha_entrega, fecha_devolucion, estado, loan_id))
            mysql.connection.commit()
            cursor.close()
            flash(f"Los datos del préstamo ID: {loan_id} han sido actualizados", "success")
            return redirect(url_for("ver_prestamos"))

        except Exception as e1:
            print("Error al actualizar el préstamo:", e1)

            # Connect to the database
            cursor = mysql.connection.cursor()

            # Retrieve the loan's data
            try:
                cursor.execute(
                    """
                    SELECT
                        L.order_id, 
                        L.fecha_entrega, 
                        L.fecha_devolucion, 
                        L.estado,
                        B.titulo
                    FROM 
                        Lending L
                    JOIN 
                        Book B ON L.id_book = B.id_book
                    WHERE 
                        L.order_id = %s
                    """,
                    (loan_id,),
                )
                loan = cursor.fetchone()
            except Exception as e2:
                print("No se pudieron obtener los datos del préstamo:", e2)
                return redirect(url_for("ver_prestamos"))

            cursor.close()
            flash("Error al actualizar el préstamo", "warning")
            return render_template("edit-loan.html", loan=loan)
        

@app.route("/mis-prestamos", methods=["GET"])
@login_required
def mis_prestamos():
    # Retrieve query parameters for search, ordering, and pagination
    search_term = request.args.get("search", default="")
    order = request.args.get("o", default="order_id")
    direction = request.args.get("d", default="ASC").upper()
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Limit of items per page

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Start building the SQL query
    base_query = """
    SELECT 
        L.order_id, 
        L.RUT_User, 
        L.id_book, 
        B.titulo,
        L.fecha_entrega, 
        L.fecha_devolucion, 
        L.estado 
    FROM 
        Lending L
    JOIN 
        Book B ON L.id_book = B.id_book
"""

    where_clause = f" WHERE RUT_User = '{session['user_id']}'"
    order_clause = ""

    # Add a WHERE clause if a search term is provided
    if search_term:
        where_clause += f" AND (L.order_id LIKE %s OR L.RUT_User LIKE %s OR L.id_book LIKE %s OR B.titulo LIKE %s OR L.fecha_entrega LIKE %s OR L.fecha_devolucion LIKE %s OR L.estado LIKE %s)"


    # Validate ordering parameters and add ORDER BY clause
    valid_columns = [
        "L.order_id",
        "L.RUT_User",
        "L.id_book",
        "B.titulo",
        "L.fecha_entrega",
        "L.fecha_devolucion",
        "L.estado",
    ]
    if order in valid_columns and direction in ["ASC", "DESC"]:
        order_clause = f" ORDER BY {order} {direction}"

    # Pagination clause
    pagination_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"

    # Complete SQL query for loans
    query = f"{base_query}{where_clause}{order_clause}{pagination_clause}"

    # Execute the query with parameters if needed
    try:
        if search_term:
            cursor.execute(
                query,
                (
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                ),
            )
        else:
            cursor.execute(query)
    except Exception as e:
        print("Error during query execution:", e)

    # Fetch the results
    loans = cursor.fetchall()

    # Format dates
    for loan in loans:
        loan["fecha_entrega"] = loan["fecha_entrega"].strftime("%d-%m-%Y")
        if loan["fecha_devolucion"]:
            loan["fecha_devolucion"] = loan["fecha_devolucion"].strftime("%d-%m-%Y")
    
    # Query for total count of loans (for pagination)
    count_query = "SELECT COUNT(*) FROM Lending" + where_clause
    cursor.execute(
        count_query,
        (
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
        )
        if search_term
        else (),
    )
    result = cursor.fetchone()
    total_loans = result["COUNT(*)"] if result else 0

    # Calculate total pages
    total_pages = (total_loans + per_page - 1) // per_page

    cursor.close()

    # Check if the request is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"loans": loans, "total_pages": total_pages, "current_page": page}
        )

    # Create a Pagination object
    pagination = Pagination(page=page, per_page=per_page, total_count=total_loans)

    # Render the template with fetched loans and pagination data
    return render_template("mis-prestamos.html", loans=loans, pagination=pagination)


@app.route("/solicitar-prestamo", methods=["GET"])
@login_required
def solicitar_prestamo():
    return search_books("solicitar-prestamo")


@app.route("/request-book", methods=["GET"])
@login_required
def request_book():
    # Get the book id from the query parameter
    user_rut = session['user_id']
    book_id = request.args.get("id")
    titulo = request.args.get("title")
    if not book_id:
        flash("No se proporcionó la ID del libro", "warning")
        return redirect(url_for("solicitar_prestamo"))
    
    # Get current date
    current_date = datetime.now()

    # Format date, YYYY-MM-DD
    formatted_date = current_date.strftime("%Y-%m-%d")

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Insert the request
    try:
        cursor.execute("INSERT INTO Solicitud (RUT_User, id_book, titulo_libro, fecha_solicitud) VALUES (%s, %s, %s, %s)", (user_rut, book_id, titulo, formatted_date))
        mysql.connection.commit()
    except Exception as e:
        print("No se pudo enviar la solicitud de préstamo:", e)
        flash("No se pudo enviar la solicitud de préstamo", "warning")
        return render_template("solicitar-prestamo.html")
    cursor.close()

    flash(f"Se envió la solicitud de préstamo: RUT: {rut_format(user_rut)} ID Libro: {book_id} Título: {titulo}", "success")
    return redirect(url_for("solicitar_prestamo"))    


@app.route("/ver-solicitudes", methods=["GET"])
@admin_required
def ver_solicitudes():
    # Retrieve query parameters for search, ordering, and pagination
    search_term = request.args.get("search", default="")
    order = request.args.get("o", default="solicitud_id")
    direction = request.args.get("d", default="ASC").upper()
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Limit of items per page

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Start building the SQL query
    base_query = "SELECT * FROM Solicitud"
    where_clause = ""
    order_clause = ""

    # Add a WHERE clause if a search term is provided
    if search_term:
        where_clause = " WHERE solicitud_id LIKE %s OR titulo_libro LIKE %s"

    # Validate ordering parameters and add ORDER BY clause
    valid_columns = ["solicitud_id", "RUT_User", "id_book", "titulo_libro", "fecha_solicitud"]
    if order in valid_columns and direction in ["ASC", "DESC"]:
        order_clause = f" ORDER BY {order} {direction}"

    # Pagination clause
    pagination_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"

    # Complete SQL query for solicituds
    query = f"{base_query}{where_clause}{order_clause}{pagination_clause}"

    # Execute the query with parameters if needed
    try:
        if search_term:
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute(query)
    except Exception as e:
        print("Error during query execution:", e)

    # Fetch the results
    solicituds = cursor.fetchall()
    
    # Format dates
    for solicitud in solicituds:
        solicitud["fecha_solicitud"] = solicitud["fecha_solicitud"].strftime("%d-%m-%Y")

    # Query for total count of solicituds (for pagination)
    count_query = "SELECT COUNT(*) FROM Solicitud" + where_clause
    cursor.execute(count_query, (f"%{search_term}%", f"%{search_term}%") if search_term else ())
    result = cursor.fetchone()
    total_solicituds = result["COUNT(*)"] if result else 0

    # Calculate total pages
    total_pages = (total_solicituds + per_page - 1) // per_page

    cursor.close()

    # Check if the solicitud is an AJAX solicitud
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"solicituds": solicituds, "total_pages": total_pages, "current_page": page}
        )

    # Create a Pagination object
    pagination = Pagination(page=page, per_page=per_page, total_count=total_solicituds)

    # Render the template with the fetched solicituds and pagination data
    return render_template("ver-solicitudes.html", solicituds=solicituds, pagination=pagination)


if __name__ == "__main__":
    app.run(debug=True)
