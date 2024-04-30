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
        permission (str, optional): The user's permission level (e.g., "normal" or "admin").
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


def search_items(template_name):
    # Retrieve query parameters for search, ordering, and pagination
    search_term = request.args.get("search", default="")
    order = request.args.get("o", default="id_item")
    direction = request.args.get("d", default="ASC").upper()
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Limit of items per page

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Start building the SQL query
    base_query = "SELECT * FROM Item"
    where_clause = ""
    order_clause = ""

    # Add a WHERE clause if a search term is provided
    if search_term:
        where_clause = " WHERE nombre LIKE %s"

    # Validate ordering parameters and add ORDER BY clause
    valid_columns = ["id_item", "nombre", "marca", "fecha_de_vencimiento", "categoria", "stock"]
    if order in valid_columns and direction in ["ASC", "DESC"]:
        order_clause = f" ORDER BY {order} {direction}"

    # Pagination clause
    pagination_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"

    # Complete SQL query for items
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
    items = cursor.fetchall()
    
    # Format dates
    for item in items:
        item["fecha_de_vencimiento"] = item["fecha_de_vencimiento"].strftime("%d-%m-%Y")

    # Query for total count of items (for pagination)
    count_query = "SELECT COUNT(*) FROM Item" + where_clause
    cursor.execute(count_query, (f"%{search_term}%",) if search_term else ())
    result = cursor.fetchone()
    total_items = result["COUNT(*)"] if result else 0

    # Calculate total pages
    total_pages = (total_items + per_page - 1) // per_page

    cursor.close()

    # Check if the request is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"items": items, "total_pages": total_pages, "current_page": page}
        )

    # Create a Pagination object
    pagination = Pagination(page=page, per_page=per_page, total_count=total_items)

    # Render the template with the fetched items and pagination data
    return render_template(f"{template_name}.html", items=items, pagination=pagination)


# Route functions
@app.route("/")
@login_required
def index():
    """Show InvenTech's homepage"""
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
        
        # Remember name of the user logged in
        session["name"] = rows[0]["nombre"]

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


@app.route("/stock", methods=["GET"])
def stock():
    return search_items("stock")


@app.route("/agregar-items", methods=["GET", "POST"])
@admin_required
def agregar_item():
    if request.method == "GET":
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("agregar-items.html")
    else:
        if not request.form.get("nombre"):
            flash(
                "Se debe introducir título.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-items.html")
        elif not request.form.get("marca"):
            flash(
                "Se debe introducir marca.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-items.html")
        elif not request.form.get("fecha_de_vencimiento"):
            flash("Se debe introducir fecha de vencimiento.\nTodos los campos son obligarios", "warning")
            render_template("agregar-items.html")
        elif not request.form.get("categoria"):
            flash(
                "Se debe introducir categoría.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-items.html")
        elif not request.form.get("stock"):
            flash(
                "Se debe introducir stock.\nTodos los campos son obligarios", "warning"
            )
            render_template("agregar-items.html")
        # User reached route via POST (as by submitting a form)
        nombre = request.form.get("nombre")
        marca = request.form.get("marca")
        fecha_de_vencimiento = request.form.get("fecha_de_vencimiento")
        categoria = request.form.get("categoria")
        stock = request.form.get("stock")
        print(nombre, marca, fecha_de_vencimiento, categoria, stock)

        cursor = mysql.connection.cursor()
        try:
            # Asegúrate de que los nombres de las columnas en la consulta coincidan con tu esquema de DB
            query = "INSERT INTO Item (nombre, marca, fecha_de_vencimiento, categoria, stock) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (nombre, marca, fecha_de_vencimiento, categoria, stock))
        except Exception as e:
            print("No se pudo registrar el item:", e)
            flash("No se pudo registrar el item.", "warning")
            return render_template("agregar-items.html")

        mysql.connection.commit()
        cursor.close()

        # Flash item creation success
        flash(
            f"Item creado correctamente.\nNombre: {nombre}\nMarca: {marca}\nFecha de vencimiento: {fecha_de_vencimiento}\nCategoría: {categoria}\nStock: {stock}",
            "success",
        )
        return render_template("agregar-items.html")


@app.route("/editar-items", methods=["GET"])
@admin_required
def editar_items():
    return search_items("editar-items")


@app.route("/edit-item", methods=["GET", "POST"])
@admin_required
def edit_item():
    if request.method == "GET":
        # Get the item ID from the query parameter
        item_id = request.args.get("id")
        if not item_id:
            flash("No se proporcionó la ID del item", "warning")
            return redirect(url_for("editar_items"))

        # Connect to the database
        cursor = mysql.connection.cursor()

        # Retrieve the item's data
        try:
            cursor.execute(
                "SELECT id_item, nombre, marca, fecha_de_vencimiento, categoria, stock FROM Item WHERE id_item = %s",
                (item_id,),
            )
            item = cursor.fetchone()
        except Exception as e:
            print("No se pudieron obtener los datos del item:", e)
            flash("No se pudieron obtener los datos del item", "warning")
            return redirect(url_for("editar_items"))

        cursor.close()

        # Check if the item exists
        if not item:
            flash("Item no encontrado", "warning")
            return redirect(url_for("editar_items"))

        # Render the edit-item.html template passing the item's data
        return render_template("edit-item.html", item=item)
    else:
        # POST request logic for updating item details
        try:
            # Retrieve the item ID and form data
            item_id = request.form.get("id_item")
            nombre = request.form.get("nombre")
            marca = request.form.get("marca")
            fecha_de_vencimiento = request.form.get("fecha_de_vencimiento")
            categoria = request.form.get("categoria")
            stock = request.form.get("stock")

            # Check if the item exists
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id_item FROM Item WHERE id_item = %s", (item_id,))
            if cursor.fetchone() is None:
                cursor.close()
                flash("Item no encontrado", "warning")
                return redirect(url_for("editar_items"))

            # Update the item's data
            update_query = """
                UPDATE Item
                SET nombre = %s, marca = %s, fecha_de_vencimiento = %s, categoria = %s, stock = %s
                WHERE id_item = %s
            """
            cursor.execute(update_query, (nombre, marca, fecha_de_vencimiento, categoria, stock, item_id))
            mysql.connection.commit()
            cursor.close()
            flash(f"Los datos del item ID: {item_id} han sido actualizados", "success")
            return redirect(url_for("editar_items"))

        except Exception as e1:
            print("Error al actualizar el item:", e1)

            # Connect to the database
            cursor = mysql.connection.cursor()

            # Retrieve the item's data
            try:
                cursor.execute(
                    "SELECT id_item, nombre, marca, fecha_de_vencimiento, categoria, stock FROM Item WHERE id_item = %s",
                    (item_id,),
                )
                item = cursor.fetchone()
            except Exception as e2:
                print("No se pudieron obtener los datos del item:", e2)
                return redirect(url_for("editar_items"))

            cursor.close()
            flash("Error al actualizar el item", "warning")
            return render_template("edit-item.html", item=item)


@app.route("/delete-item", methods=["GET"])
@admin_required
def delete_item():
    # Get the item ID from the query parameter
    item_id = request.args.get("id")
    if not item_id:
        flash("No se proporcionó la ID del item", "warning")
        return redirect(url_for("editar_items"))

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Delete the item by item id
    try:
        cursor.execute("DELETE FROM Item WHERE id_item = %s", (item_id,))
        mysql.connection.commit()
    except Exception as e:
        print("No se pudo eliminar el item:", e)
        flash("No se pudo eliminar el item", "warning")
        return render_template("editar-items.html")
    cursor.close()

    flash(f"Se eliminó el item ID: {item_id}", "success")
    return redirect(url_for("editar_items"))


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
        cursor.execute("DELETE FROM User WHERE RUT = %s", (user_rut,))
        mysql.connection.commit()
    except Exception as e:
        print("No se pudo eliminar el usuario:", e)
        flash("No se pudo eliminar el usuario", "warning")
        return render_template("editar-usuarios.html")
    cursor.close()

    flash(f"Se eliminó el usuario RUT: {rut_format(user_rut)}", "success")
    return redirect(url_for("editar_usuarios"))


if __name__ == "__main__":
    app.run(debug=True)
