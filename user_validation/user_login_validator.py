def validate_login_input(rut=None, password=None):
    """Validate user input for login.

    Args:
        rut (str, optional): The user's RUT.
        password (str, optional): The user's password.

    Returns:
        list: A list of error messages, if any.

    """
    errors = []

    # Basic validations
    if not rut:
        errors.append("Se debe ingresar el RUT")
    if not password:
        errors.append("Se debe ingresar la contraseña")

    return errors
