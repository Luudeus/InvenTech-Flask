import re


def format_rut(rut):
    """
    Remove dots and hyphens from a Chilean RUT (Rol Único Tributario).

    Parameters:
    rut (str): A string representing a Chilean RUT.

    Returns:
    str: The RUT with dots and hyphens removed.
    """
    rut = rut.replace(".", "").replace("-", "")
    return rut


def format_mail(mail):
    """
    Remove all spaces from an email address. Note: This function is not typically
    used for email validation or normalization as periods can be significant.

    Parameters:
    mail (str): A string representing an email address.

    Returns:
    str: The email address with spaces removed.
    """
    mail = mail.replace(" ", "")
    return mail


def format_name(name):
    """
    Format a name by removing non-alphabetic characters, converting the first
    letter of each word to uppercase, and trimming whitespace from the ends.

    Parameters:
    name (str): A string representing a person's name.

    Returns:
    str: The formatted name.
    """
    # Remove all characters that are not letters or spaces (including accented characters)
    name = re.sub(r"[^a-zA-ZÀ-ÖØ-öø-ÿ\s]", "", name)

    # Convert the first letter of each word to uppercase
    name = name.title()

    # Then, trim spaces at the beginning and the end
    name = name.strip()

    return name


def format_data(rut, mail, name):
    """
    Format the RUT, email, and name using the respective formatting functions.

    Parameters:
    rut (str): A string representing a Chilean RUT.
    mail (str): A string representing an email address.
    name (str): A string representing a person's name.

    Returns:
    tuple: A tuple containing the formatted RUT, email, and name.
    """
    rut = format_rut(rut)
    mail = format_mail(mail)
    name = format_name(name)
    return rut, mail, name


if __name__ == "__main__":
    def main():
        # Example usage of the format_data function
        formatted_rut, formatted_mail, formatted_name = format_data("12.345.678-9", "example.mail@domain.com", " JOHN DOE ")
        print(f"Formatted RUT: {formatted_rut}")
        print(f"Formatted email: {formatted_mail}")
        print(f"Formatted name: {formatted_name}")

    main()
