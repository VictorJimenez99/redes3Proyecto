function ConfidEdit(id) {
    let SendInfo = {
        key: $("#sys_key").val(),
        new_value: $("#sys_unit").val(),
    };

    $.ajax({
        type: 'post',
        url: '/sys_config_update',
        data: JSON.stringify(SendInfo),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (data) {
            createAlert('Exito!', 'Se ha modificado', 'El modificado con exito', 'success', true, true, 'pageMessages');
            setTimeout(function () {
                $(location).attr('href', '/sys_config_view');
            }, 1000);

        },
        error: function (xhr) {
            console.log(xhr)
            createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
        }
    });

}

