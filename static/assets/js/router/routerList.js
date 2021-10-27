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

