$(document).ready(function () {


    $("#btn_crear").click(function () {
        let ip = $("#name").find(':selected').data('ip');
        let protocol = $("#protocol").val();
        let router_user  = $("#access_user").val();
        let netwotks =$("#networks").tagsinput('items');
        console.log(netwotks);
        let router_user_password = $("#access_password").val();
        let nombre_proto =   $("#nombre_proto").val();

        return


        $("#name").attr("disabled", "disabled");
        $("#ip_addr").attr("disabled", "disabled");
        $("#protocol").attr("disabled", "disabled");
        if (ip_addr === "" || name === "") {
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
            let ruta = null
            if (protocol == 1) {
                ruta = "/router/<string:router_ip>/router_rip";
            }

            $.ajax({
                type: 'post',
                url: ruta,
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


function onChengeProtocol(select) {
    let valor = select.value;
    console.log(valor)
    if (valor == 2 || valor == 3) {
        $("#nombre_proto").parent().show();
        $("#nombre_proto").parent().removeClass("d-none");
        if (valor == 2) {
            $('#nombre_proto').attr('placeholder', 'Identificador de ospf');
            $('.bootstrap-tagsinput input').attr('placeholder', ' Grupos de 3 (id de la red) (wildcard) (numero de area)');
        } else {
            $('#nombre_proto').attr('placeholder', 'autonomous-system (numero)');
            $('.bootstrap-tagsinput input').attr('placeholder', 'Cada ip de la network a configurar\'');
        }
    } else {
        $("#nombre_proto").parent().removeAttr("style").hide();
        $('.bootstrap-tagsinput input').attr('placeholder', 'Cada ip de la network a configurar');
    }
}


function onChengeRouter(select) {

    if (select.value != -1) {
        protocol = $("#name").find(':selected').data('protocol');
        $("#protocol").val(protocol).change();

    }


}