(function($) {
    $(document).ready(function() {
        const $sectorField = $('#id_sector');
        const $areaField = $('#id_area');
        const $warehouseField = $('#id_warehouse');

        // Отключаем выбор сектора и области, пока склад не выбран
        $sectorField.prop('disabled', true);
        $areaField.prop('disabled', true);

        // Обновляем области при изменении склада
        $warehouseField.on('change', function() {
            const warehouseId = $(this).val();
            if (!warehouseId) {
                $areaField.prop('disabled', true).empty();
                $sectorField.prop('disabled', true).empty();
                return;
            }

            // Загружаем области через AJAX
            const areaUrl = `/admin/warehouse-areas/?warehouse_id=${warehouseId}`;
            $.ajax({
                url: areaUrl,
                success: function(data) {
                    $areaField.empty();
                    $areaField.append(`<option value="">---------</option>`);
                    for (const [id, text] of Object.entries(data)) {
                        $areaField.append(`<option value="${id}">${text}</option>`);
                    }
                    $areaField.prop('disabled', false);
                    $sectorField.prop('disabled', true).empty(); // Очищаем сектора
                }
            });
        });

        // Обновляем сектора при изменении области
        $areaField.on('change', function() {
            const areaId = $(this).val();
            if (!areaId) {
                $sectorField.prop('disabled', true).empty();
                return;
            }

            // Загружаем сектора через AJAX
            const sectorUrl = `/admin/area-sectors/?area_id=${areaId}`;
            $.ajax({
                url: sectorUrl,
                success: function(data) {
                    $sectorField.empty();
                    $sectorField.append(`<option value="">---------</option>`);
                    for (const [id, text] of Object.entries(data)) {
                        $sectorField.append(`<option value="${id}">${text}</option>`);
                    }
                    $sectorField.prop('disabled', false);
                }
            });
        });
    });
})(django.jQuery);
