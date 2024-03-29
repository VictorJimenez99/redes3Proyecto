$(document).ready(function () {
    $("#btn_crear").click(function () {

        let name = $("#user_name").val();
        let password = $("#password").val();
        let user_type = $("#user_type").val();
        let access_user = $("#access_user").val();
        let access_password = $("#access_password").val();
        $("#user_name").attr("disabled", "disabled");
        $("#password").attr("disabled", "disabled");
        $("#user_type").attr("disabled", "disabled");
        $("#access_user").attr("disabled", "disabled");
        $("#access_password").attr("disabled", "disabled");
        if (user_type === "-1" || name === "" || password === "") {
            alert("Llenar datos requeridos")
            $("#password").removeAttr("disabled");
            $("#user_name").removeAttr("disabled");
            $("#user_type").removeAttr("disabled");
            $("#access_user").removeAttr("disabled");
            $("#access_password").removeAttr("disabled");
        } else {
            let SendInfo = {
                user_name: name,
                password: password,
                user_type: user_type,
                access_user: access_user,
                access_password: access_password
            };

            $.ajax({
                type: 'post',
                url: '/add_router_user',
                data: JSON.stringify(SendInfo),
                contentType: "application/json; charset=utf-8",
                traditional: true,
                success: function (data) {

                    createAlert('Exito!', 'Se ha creado', 'El usuario a sido creado exitosamente', 'success', true, true, 'pageMessages');
                    setTimeout(function () {
                        $(location).attr('href', '/router_user_list');
                    }, 3000);

                },
                error: function (xhr) {
                    $("#password").removeAttr("disabled");
                    $("#user_name").removeAttr("disabled");
                    $("#user_type").removeAttr("disabled");
                    $("#access_user").removeAttr("disabled");
                    $("#access_password").removeAttr("disabled");
                    createAlert('Opps!', 'Something went wrong', xhr.responseText, 'danger', true, true, 'pageMessages');
                }
            });
        }


    })

});


