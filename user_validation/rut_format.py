def rut_format(rut):
    # Limpiar el RUT de caracteres no deseados y asegurarse de que 'k' sea mayúscula
    cleaned_rut = ''.join(filter(lambda x: x.isdigit() or x.lower() == 'k', rut)).upper()

    if cleaned_rut and len(cleaned_rut) > 1:
        # Extraer la parte numérica y el dígito verificador
        numeric_part = cleaned_rut[:-1]
        dv = cleaned_rut[-1]

        # Limitar la longitud de la parte numérica a 9 caracteres
        numeric_part = numeric_part[:9]

        # Dar formato a la parte numérica
        formatted_rut = '.'.join([numeric_part[max(i-3, 0):i] for i in range(len(numeric_part), 0, -3)][::-1])

        # Combinar la parte numérica formateada con el dígito verificador
        formatted_rut += '-' + dv

        return formatted_rut

    return cleaned_rut
