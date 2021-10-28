let placeholder = "";
$(document).ready(function () {

    $(".bootstrap-tagsinput input:first-child").attr("size", 60);
    placeholder = $(".bootstrap-tagsinput input").attr("placeholder");
    $("#networks").on('beforeItemAdd', function (event) {

        if ($("#networks").tagsinput('items').length == 1) {
            placeholder = $(".bootstrap-tagsinput input").attr("placeholder");
        }
        $(".bootstrap-tagsinput input:first-child").removeAttr("placeholder");
    });
    $("#networks").on('beforeItemRemove', function (event) {
        console.log($("#networks").tagsinput('items').length);
        if ($("#networks").tagsinput('items').length == 1) {
            console.log(placeholder);
            $(".bootstrap-tagsinput input").attr("placeholder", placeholder);
        }

    });


    $("#btn_crear").click(function () {
        let ip_addr = $("#name").find(':selected').data('ip');
        let protocol = $("#protocol").val();
        let router_user = $("#access_user").val();
        let networks = $("#networks").tagsinput('items');
        let proto_name = $("#nombre_proto").val();
        console.log(networks);
        let router_user_password = $("#access_password").val();


        $("#name").attr("disabled", "disabled");
        $("#protocol").attr("disabled", "disabled");
        $("#access_user").attr("disabled", "disabled");
        $("#networks").attr("disabled", "disabled");
        $("#access_password").attr("disabled", "disabled");
        $("#nombre_proto").attr("disabled", "disabled");

        if (ip_addr === "" || protocol === "" || router_user === "" || !(networks.length > 0)) {
            alert("Llenar datos requeridos")
            $("#name").removeAttr("disabled");
            $("#protocol").removeAttr("disabled");
            $("#access_user").removeAttr("disabled");
            $("#networks").removeAttr("disabled");
            $("#access_password").removeAttr("disabled");
            $("#nombre_proto").removeAttr("disabled");
        } else {
            let ruta = null
            let SendInfo = null;
            if (protocol == 1) {
                ruta = "/router/" + ip_addr + "/router_rip";
                SendInfo = {
                    router_user: router_user,
                    router_user_password: router_user_password,
                    networks: networks,
                }

            } else if (protocol == 2) {
                ruta = "/router/" + ip_addr + "/router_ospf";
                if ((networks.length % 3) !== 0) {
                    alert("Formato de las ip de network no funcionan")
                    return
                }
                let networkFixed = [];
                for (let i = 1; i <= networks.length; i++) {
                    if (i % 3 === 0) {
                        networkFixed.push({
                            ip_network: networks[i - 3],
                            wildcard: networks[i - 2],
                            num_area: networks[i - 1],
                        });
                    }
                }
                console.log(networkFixed);

                SendInfo = {
                    router_user: router_user,
                    router_user_password: router_user_password,
                    proto_name: proto_name,
                    networks: networkFixed,
                }

            } else if (protocol == 3) {
                ruta = "/router/" + ip_addr + "/router_eigrp";
                SendInfo = {
                    router_user: router_user,
                    router_user_password: router_user_password,
                    networks: networks,
                    proto_name: proto_name,
                }

            }

            console.log(SendInfo);


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
                    $("#protocol").removeAttr("disabled");
                    $("#access_user").removeAttr("disabled");
                    $("#networks").removeAttr("disabled");
                    $("#access_password").removeAttr("disabled");
                    $("#nombre_proto").removeAttr("disabled");
                    createAlert('Opps!', 'Something went wrong', xhr.responseText, 'danger', true, true, 'pageMessages');

                }
            });
        }


    })
});


function onChangeProtocol(select) {
    let valor = select.value;
    console.log(valor)
    if (valor == 2 || valor == 3) {
        $("#nombre_proto").parent().show();
        $("#nombre_proto").parent().removeClass("d-none");
        if (valor == 2) {
            $('#nombre_proto').attr('placeholder', 'Identificador de ospf');
            placeholder = "Grupos de 3 (id de la red) (wildcard) (numero de area)";
            $('.bootstrap-tagsinput input').attr('placeholder', placeholder);
        } else {
            placeholder = "Cada ip de la network a configurar";
            $('#nombre_proto').attr('placeholder', 'autonomous-system (numero)');
            $('.bootstrap-tagsinput input').attr('placeholder', placeholder);
        }
    } else {
        $("#nombre_proto").parent().removeAttr("style").hide();
        placeholder = "Cada ip de la network a configurar";
        $('.bootstrap-tagsinput input').attr('placeholder', placeholder);
    }
}


function onChangeRouter(select) {

    if (select.value != -1) {
        protocol = $("#name").find(':selected').data('protocol');
        $("#protocol").val(protocol).change();

    }


}