/**
 * ==========================================
 * VALIDACIÓN Y FORMATEO DE RUT CHILENO
 * ==========================================
 * 
 * Este archivo contiene funciones para validar y formatear el RUT chileno
 * utilizando el algoritmo del módulo 11.
 */

/**
 * Calcula el dígito verificador de un RUT
 * @param {string} rutNumeros - Los números del RUT sin el dígito verificador
 * @returns {string} El dígito verificador calculado ('0'-'9' o 'K')
 */
function calcularDV(rutNumeros) {
    if (!rutNumeros || rutNumeros.length < 7 || isNaN(rutNumeros)) {
        return '';
    }

    let suma = 0;
    let multiplicador = 2;

    // Algoritmo del módulo 11
    for (let i = rutNumeros.length - 1; i >= 0; i--) {
        suma += parseInt(rutNumeros[i]) * multiplicador;
        multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
    }

    const resto = suma % 11;
    const dv = 11 - resto;

    if (dv === 11) return '0';
    if (dv === 10) return 'K';
    return dv.toString();
}

/**
 * Valida un RUT completo (números + dígito verificador)
 * @param {string} rutNumeros - Los números del RUT sin el dígito verificador
 * @param {string} rutDV - El dígito verificador del RUT
 * @returns {boolean} true si el RUT es válido, false en caso contrario
 */
function validarRutCompleto(rutNumeros, rutDV) {
    if (!rutNumeros || rutNumeros.length < 7 || isNaN(rutNumeros) || rutDV === '') {
        return false;
    }

    const dvEsperado = calcularDV(rutNumeros);
    return dvEsperado.toLowerCase() === rutDV.toLowerCase();
}

/**
 * Formatea un RUT agregando puntos y guion
 * @param {string} value - El RUT completo sin formato (números + DV)
 * @returns {string} El RUT formateado (ej: "12.345.678-9")
 */
function formatRut(value) {
    // Limpia caracteres no válidos
    const cleanValue = value.replace(/[^0-9kK]/g, '');
    if (cleanValue.length === 0) return '';

    // Separa el cuerpo del RUT y el dígito verificador
    const cuerpo = cleanValue.slice(0, -1);
    const dv = cleanValue.slice(-1).toUpperCase();

    // Añade puntos como separadores de miles
    const cuerpoFormateado = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    return `${cuerpoFormateado}-${dv}`;
}

/**
 * Inicializa la validación de RUT en un formulario de creación
 * @param {string} rutNumerosId - ID del campo de números del RUT
 * @param {string} rutDVId - ID del campo del dígito verificador
 * @param {string} statusIconId - ID del elemento que muestra el icono de estado
 */
function inicializarValidacionRUT(rutNumerosId, rutDVId, statusIconId) {
    const rutNumerosInput = document.getElementById(rutNumerosId);
    const rutDVInput = document.getElementById(rutDVId);
    const statusIcon = document.getElementById(statusIconId);

    if (!rutNumerosInput || !rutDVInput || !statusIcon) {
        console.error('No se encontraron los elementos necesarios para validación de RUT');
        return;
    }

    rutNumerosInput.addEventListener('input', function() {
        // Limpia cualquier caracter que no sea un número
        const rutNumeros = this.value.replace(/\D/g, '');
        this.value = rutNumeros.slice(0, 8); // Limita a 8 dígitos

        // Si el RUT es muy corto, no calcula el DV
        if (!rutNumeros || rutNumeros.length < 7) {
            rutDVInput.value = '';
            statusIcon.textContent = '✖';
            statusIcon.style.color = 'red';
            return;
        }

        // Calcula y asigna el dígito verificador
        const dv = calcularDV(rutNumeros);
        rutDVInput.value = dv;

        // Actualiza el ícono de estado
        if (validarRutCompleto(rutNumeros, dv)) {
            statusIcon.textContent = '✔';
            statusIcon.style.color = 'green';
        } else {
            statusIcon.textContent = '✖';
            statusIcon.style.color = 'red';
        }
    });
}

/**
 * Formatea un campo de RUT de solo lectura (para edición)
 * @param {string} rutInputId - ID del campo de RUT
 */
function formatearRutReadonly(rutInputId) {
    const rutInput = document.getElementById(rutInputId);
    if (!rutInput) return;

    const value = rutInput.value.replace(/[^0-9kK]/g, '');
    if (value.length === 0) return;

    const cuerpo = value.slice(0, -1);
    const dv = value.slice(-1);
    const cuerpoFormateado = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    rutInput.value = `${cuerpoFormateado}-${dv}`;
}

/**
 * Formatea todos los elementos con una clase específica (para tablas)
 * @param {string} className - Clase CSS de los elementos a formatear
 */
function formatearRutsEnTabla(className) {
    const rutElements = document.querySelectorAll(`.${className}`);
    rutElements.forEach(element => {
        element.textContent = formatRut(element.textContent.trim());
    });
}

/**
 * Valida un nombre (solo letras y espacios)
 * @param {string} nombre - El nombre a validar
 * @returns {boolean} true si el nombre es válido
 */
function validarNombre(nombre) {
    const regex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
    return regex.test(nombre);
}

/**
 * Inicializa la validación de nombre
 * @param {string} nombreId - ID del campo de nombre
 * @param {string} statusIconId - ID del elemento que muestra el icono de estado
 */
function inicializarValidacionNombre(nombreId, statusIconId) {
    const nombreInput = document.getElementById(nombreId);
    const statusIcon = document.getElementById(statusIconId);

    if (!nombreInput || !statusIcon) {
        console.error('No se encontraron los elementos necesarios para validación de nombre');
        return;
    }

    nombreInput.addEventListener('input', function() {
        const nombre = this.value;

        if (validarNombre(nombre)) {
            statusIcon.textContent = '✔';
            statusIcon.style.color = 'green';
        } else {
            statusIcon.textContent = '✖';
            statusIcon.style.color = 'red';
        }
    });
}
