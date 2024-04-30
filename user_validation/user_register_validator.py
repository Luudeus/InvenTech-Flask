import re
from werkzeug.security import generate_password_hash


def validate_register_input(
    rut=None, name=None, mail=None, password=None, confirmation=None, permission=None
):
    """Validate user input for registration.

    Args:
        rut (str, optional): The user's RUT.
        name (str, optional): The user's name.
        mail (str, optional): The user's email.
        password (str, optional): The user's password.
        confirmation (str, optional): The password confirmation.

    Returns:
        list: A list of error messages, if any.

    """
    errors = []

    # Basic validations
    if not rut:
        errors.append("Se debe ingresar el RUT")
    if not name:
        errors.append("Se debe ingresar el nombre")
    if not mail:
        errors.append("Se debe ingresar el correo")
    if not password:
        errors.append("Se debe ingresar la contraseña")
    if not confirmation:
        errors.append("Se debe re-ingresar la contraseña")
    # Mail complexity validation
    if not is_email_complex(mail):
        errors.append(
            "El correo debe estar en un formato correcto. Ejemplo: 'example@example.com'"
        )
    # Check if passwords match
    if not passwords_match(password, confirmation):
        errors.append("La contraseña y la contraseña de confirmación no coinciden")

    # Password complexity validation
    if not is_password_complex(password):
        errors.append("La contraseña debe contener al menos 3 letras y 2 dígitos")

    # Check if permission is correct
    if permission:
        if not is_permission_valid(permission):
            errors.append("Tipo de permiso inválido")
            
    return errors


def is_password_complex(password):
    """Check if the password meets complexity requirements.

    Args:
        password (str): The user's password.

    Returns:
        bool: True if the password meets complexity requirements, False otherwise.

    """
    digits = re.findall(r"\d", password)
    letters = re.findall(r"[A-Za-z]", password)
    return len(digits) >= 2 and len(letters) >= 3


def is_email_complex(email):
    """Check if the email address meets complexity requirements.

    Args:
        email (str): The user's email address.

    Returns:
        bool: True if the email meets complexity requirements, False otherwise.

    """
    # Check if email is None
    if email is None or not isinstance(email, str):
        return False
    
    # Check if the email contains only one "@" character
    if email.count("@") != 1:
        return False

    # Split the email into username and domain
    username, domain = email.split("@")

    # Check if the username and domain meet complexity requirements
    if len(username) < 1 or len(domain) < 1:
        return False

    # Check if the domain contains at least one "." character
    if "." not in domain:
        return False

    return True


def is_permission_valid(permission):
    """Check if the permission is in the list of permissions.

    Args:
        permission (str): The user's permissions type.

    Returns:
        bool: True if the permission is in permissions list, False otherwise.

    """
    permissions = ["normal", "bibliotecario"]
    return permission in permissions


def passwords_match(password, confirmation):
    """Check if the password and confirmation password match.

    Args:
        password (str): The user's password.
        confirmation (str): The user's confirmation password.

    Returns:
        bool: True if the password match, False otherwise.

    """
    return password == confirmation


def hash_password(password):
    """Generate a password hash.

    Args:
        password (str): The user's password.

    Returns:
        str: The hashed password.

    """
    return generate_password_hash(password)
