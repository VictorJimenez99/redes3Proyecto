$(document).ready(function () {
    $("#btn_crear").click(function () {

        let name = $("#user_name").val();
        let password = $("#password").val();
        let user_type = $("#user_type").val();
        $("#user_name").attr("disabled", "disabled");
        $("#password").attr("disabled", "disabled");
        $("#user_type").attr("disabled", "disabled");
        if (user_type === "-1"|| name==="" || password==="") {
            alert("Llenar datos requeridos")
            $("#password").removeAttr("disabled");
            $("#user_name").removeAttr("disabled");
            $("#user_type").removeAttr("disabled");
        } else {
            let SendInfo = {
                new_name: name,
                new_password: password,
                user_type: user_type
            };

            $.ajax({
                type: 'post',
                url: '/add_sys_user',
                data: JSON.stringify(SendInfo),
                contentType: "application/json; charset=utf-8",
                traditional: true,
                success: function (data) {

                    createAlert('Exito!', 'Se ha creado', 'El usuario a sido creado exitosamente', 'success', true, true, 'pageMessages');
                    setTimeout(function () {
                        $(location).attr('href', '/app_user_list');
                    }, 3000);

                },
                error: function (xhr) {
                    $("#password").removeAttr("disabled");
                    $("#user_name").removeAttr("disabled");
                    $("#user_type").removeAttr("disabled");
                    createAlert('Opps!', 'Something went wrong', xhr.responseText, 'danger', true, true, 'pageMessages');

                }
            });
        }


    })

});

function updateEmail(email) {
    let SendInfo = {
        new_email: email
    };

    $.ajax({
        type: 'post',
        url: '/change_email_sys_user',
        data: JSON.stringify(SendInfo),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (data) {
            createAlert('Exito!', 'Se ha actualizado', 'El correo electronico ha sido actualizado, ahora recibiras las notificaciones a ' + email, 'success', true, true, 'pageMessages');
            setTimeout(function () {
                $(location).attr('href', '/');
            }, 5000);

        },
        error: function (xhr) {
            createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
        }
    });

}