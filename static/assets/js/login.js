$(document).ready(function () {

    $("#inicia_sesion").click(function () {

        let name = $("#nombre").val();
        let password = $("#password").val();

        let SendInfo = {
            name: name,
            password: password
        };

        $.ajax({
            type: 'post',
            url: '/create_session',
            data: JSON.stringify(SendInfo),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                 $(location).attr('href', '/');
            },
            error: function (xhr) {
                if(xhr.responseText==="Invalid_Credentials"){
                  createAlert('Opps!', 'Something went wrong', xhr.responseText, 'danger', true, true, 'pageMessages');
                }else{
                    createAlert('Opps!', 'Something went wrong', 'please contact system support assistance', 'danger', true, true, 'pageMessages');

                }

//                alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
            }
        });


    })


});

