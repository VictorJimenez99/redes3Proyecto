$(document).ready(function () {


})

function dropRouter(id){
            let SendInfo = {
            id: id
        };

        $.ajax({
            type: 'post',
            url: '/drop_router',
            data: JSON.stringify(SendInfo),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                createAlert('Exito!', 'Se ha eliminado', 'El ruouter se a eliminado exitosamente', 'success', true, true, 'pageMessages');
                setTimeout(function () {
                    $(location).attr('href', '/router_list');
                }, 1000);

            },
            error: function (xhr) {
                console.log(xhr)
                createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
            }
        });

}


function snmpEdit() {
    let SendInfo = {
        router_name: $("#router_name").val(),
        snmp_key: $("#snmp_key").val(),
        snmp_new_value: $("#snmp_new_value").val()
    };

    $.ajax({
        type: 'post',
        url: '/set_snmp',
        data: JSON.stringify(SendInfo),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (data) {
            createAlert('Exito!', 'Se ha modificado', 'El modificado con exito', 'success', true, true, 'pageMessages');
            setTimeout(function () {
                $(location).attr('href', '/router_list');
            }, 1000);

        },
        error: function (xhr) {
            console.log(xhr)
            createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
        }
    });

}

function openModal() {
    $('#modelDelete').modal('show')
}

function closeModal() {
    $('#modelDelete').modal('hide')
}


function setSnmpInfo(sys_name, sys_contact, sys_location) {
    $("#modal_sys_name").html("sys_name: "+sys_name);
    $("#modal_sys_contact").html("sys_contact: "+sys_contact);
    $("#modal_sys_location").html("sys_location: "+sys_location);
}
