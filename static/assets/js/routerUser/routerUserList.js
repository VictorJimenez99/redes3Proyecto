$(document).ready(function () {


})
let param_id = null;

function dropRouterUser(id) {
    let access_password = $("#access_password").val();
    let access_user = $("#access_user").val();
    if(access_user==="-1"|| access_password===undefined){
        alert("Colocar credenciales");
        return
    }
    let SendInfo = {
        id: id,
        access_password: access_password,
        access_user: access_user
    };

    $.ajax({
        type: 'post',
        url: '/drop_router_user',
        data: JSON.stringify(SendInfo),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (data) {
            createAlert('Exito!', 'Se ha eliminado', 'El usuario se a eliminado exitosamente', 'success', true, true, 'pageMessages');
            closeModal();
            setTimeout(function () {
                $(location).attr('href', '/router_user_list');
            }, 1000);

        },
        error: function (xhr) {
            console.log(xhr)
            closeModal();
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
function setId(id) {
    param_id = id;
}

function unsetId(id) {
    param_id = null;
}

function getId() {
    return param_id;
}



