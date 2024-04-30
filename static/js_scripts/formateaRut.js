function formateaRut(rut) {
    var actual = rut.replace(/[^0-9kK]/g, "").replace(/k/g, "K");

    if (actual != '' && actual.length > 1) {
        var sinPuntos = actual.replace(/\./g, "");
        var actualLimpio = sinPuntos.replace(/-/g, "");
        if (actualLimpio.length > 9) {
            actualLimpio = actualLimpio.slice(0, -1); // Elimina el último carácter de actualLimpio
        }
        var inicio = actualLimpio.substring(0, actualLimpio.length - 1);
        var rutPuntos = "";
        var i = 0;
        var j = 1;
        for (i = inicio.length - 1; i >= 0; i--) {
            var letra = inicio.charAt(i);
            rutPuntos = letra + rutPuntos;
            if (j % 3 == 0 && j <= inicio.length - 1) {
                rutPuntos = "." + rutPuntos;
            }
            j++;
        }
        var dv = actualLimpio.substring(actualLimpio.length - 1);
        rutPuntos = rutPuntos + "-" + dv;
        return rutPuntos.substring(0, 12); // Asegurarse de que el RUT no exceda los 12 caracteres
    }
    return actual; // Retorna el RUT procesado si no es lo suficientemente largo
}

document.getElementById('rut').addEventListener('input', function() {
    this.value = formateaRut(this.value);
});