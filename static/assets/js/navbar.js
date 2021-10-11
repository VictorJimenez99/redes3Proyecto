$(document).ready(function () {

    $("#btn_logout").click(function () {


        $.ajax({
            type: 'post',
            url: '/logout',
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                 $(location).attr('href', '/');
            },
            error: function (xhr) {
                alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
            }
        });


    })


});

