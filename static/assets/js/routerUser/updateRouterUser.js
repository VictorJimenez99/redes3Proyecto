$(document).ready(function () {
    let old_name = $("#user_name").val();
    let old_id = $("#id").val();
    $("#user_name").attr("disabled", "disabled");
    let old_password = "nopassword";
    let old_user_type = $("#user_type").val();
    $("#btn_update").click(function () {

        let name = $("#user_name").val();
        let password = $("#password").val();
        let user_type = $("#user_type").val();
        let id = $("#id").val();
        $("#password").attr("disabled", "disabled");
        $("#user_type").attr("disabled", "disabled");
        let access_password = $("#access_password").val();
        let access_user = $("#access_user").val();
        if (access_user === "-1" || access_password === undefined) {
            alert("Colocar credenciales");
            return
        }

        if (user_type === "-1" || name === "" || password === "" || (old_password === password && old_user_type === user_type)) {
            alert("Nada que modificar")
            $("#password").removeAttr("disabled");
            $("#user_type").removeAttr("disabled");
        } else if (old_name !== name || old_id !== id) {
            alert("El nombre no puede ser editado")
        } else {


            let SendInfo = {
                id: id,
                user_name: name,
                password: password,
                user_type: user_type,
                access_password: access_password,
                access_user: access_user
            };

            $.ajax({
                type: 'post',
                url: '/update_router_user',
                data: JSON.stringify(SendInfo),
                contentType: "application/json; charset=utf-8",
                traditional: true,
                success: function (data) {

                    createAlert('Exito!', 'Se ha actualizadp', 'El usuario a sido actualizado', 'success', true, true, 'pageMessages');
                    setTimeout(function () {
                        $(location).attr('href', '/router_user_list');
                    }, 2000);

                },
                error: function (xhr) {
                    $("#password").removeAttr("disabled");
                    $("#user_type").removeAttr("disabled");
                    createAlert('Opps!', 'Something went wrong', xhr.responseText, 'danger', true, true, 'pageMessages');
                }
            });
        }


    })

});


