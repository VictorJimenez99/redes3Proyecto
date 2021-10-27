$(document).ready(function () {

    $("#nombre_proto").parent().removeAttr("style").hide();

        $("#btn_crear").click(function () {

        let name = $("#name").val();
        let ip_addr = $("#ip_addr").val();
        let protocol = $("#protocol").val();

        $("#name").attr("disabled", "disabled");
        $("#ip_addr").attr("disabled", "disabled");
        $("#protocol").attr("disabled", "disabled");
        if (ip_addr==="" || name==="") {
            alert("Llenar datos requeridos")
            $("#name").removeAttr("disabled");
            $("#ip_addr").removeAttr("disabled");
            $("#protocol").removeAttr("disabled");
        } else {
            let SendInfo = {
                name: name,
                ip_addr: ip_addr,
                protocol: protocol
            };

            $.ajax({
                type: 'post',
                url: '/add_router',
                data: JSON.stringify(SendInfo),
                contentType: "application/json; charset=utf-8",
                traditional: true,
                success: function (data) {

                    createAlert('Exito!', 'Se ha creado', 'El router a sido creado exitosamente', 'success', true, true, 'pageMessages');
                    setTimeout(function () {
                        $(location).attr('href', '/router_list');
                    }, 3000);

                },
                error: function (xhr) {
                    $("#name").removeAttr("disabled");
                    $("#ip_addr").removeAttr("disabled");
                    $("#protocol").removeAttr("disabled");
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