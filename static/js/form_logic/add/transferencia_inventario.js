document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('dynamic_form');
    if (!form) return;

    const productoSelect = document.getElementById('id_producto');
    const almacenOrigenSelect = document.getElementById('id_almacen_origen');

    if (!productoSelect || !almacenOrigenSelect) return;

    function clearAlmacenesOrigen() {
        while (almacenOrigenSelect.firstChild) {
            almacenOrigenSelect.removeChild(almacenOrigenSelect.firstChild);
        }
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'Selecciona una opción';
        almacenOrigenSelect.appendChild(opt);
    }

    function loadAlmacenesOrigen(productoId) {
        clearAlmacenesOrigen();
        if (!productoId) {
            if (window.jQuery && jQuery.fn.select2) {
                jQuery(almacenOrigenSelect).val('').trigger('change');
            }
            return;
        }

        fetch(`/transferencias/almacenes_origen?producto_id=${encodeURIComponent(productoId)}`)
            .then(resp => resp.json())
            .then(data => {
                clearAlmacenesOrigen();
                data.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.id;
                    opt.textContent = item.nombre;
                    almacenOrigenSelect.appendChild(opt);
                });

                // Si solo hay un almacén con existencia, seleccionarlo automáticamente
                if (data.length === 1) {
                    almacenOrigenSelect.value = data[0].id;
                }

                if (window.jQuery && jQuery.fn.select2) {
                    jQuery(almacenOrigenSelect).trigger('change');
                }
            })
            .catch(err => {
                console.error('Error cargando almacenes de origen:', err);
            });
    }

    // Cambio de producto en alta de transferencia
    productoSelect.addEventListener('change', function () {
        const productoId = this.value;
        loadAlmacenesOrigen(productoId);
    });

    // Si ya hay un producto seleccionado al cargar (por ejemplo en edición), cargar sus almacenes
    if (productoSelect.value) {
        loadAlmacenesOrigen(productoSelect.value);
    }
});
