$(document).ready(function () {

    $("#nombre_proto").parent().removeAttr("style").hide();

        $("#btn_crear").click(function () {

        let name = $("#name").val();
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

function onCheckboxChanged(checked) {
    if (!checked) {
        $("#protocol").removeAttr("style").hide();
        $(".bootstrap-tagsinput").removeAttr("style").hide();
        $("#nombre_proto").parent().removeAttr("style").hide();

    } else {
        $("#protocol").show();
        $(".bootstrap-tagsinput").show();
        $("#nombre_proto").parent().show();

    }
}

function onChengeProtocol(select) {
    let valor = select.value;
    console.log(valor)
    if (valor == 2 || valor == 3) {
        $("#nombre_proto").parent().show();
        if (valor == 2) {
            $('#nombre_proto').attr('placeholder', 'Identificador de ospf');
            $('.bootstrap-tagsinput input').attr('placeholder', ' Grupos de 3 (id de la red) (wildcard) (numero de area)');
        } else {
            $('#nombre_proto').attr('placeholder', 'autonomous-system (numero)');
            $('.bootstrap-tagsinput input').attr('placeholder', 'Cada ip a configurar');
        }
    } else {
        $("#nombre_proto").parent().removeAttr("style").hide();
        $('.bootstrap-tagsinput input').attr('placeholder', 'Cada ip a configurar');
    }
}