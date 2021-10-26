$(document).ready(function () {

    $("#btn_logout").click(function (event) {
        event.preventDefault();

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


function clean_navbar() {
    $("#navbar a").each(function () {
        $(this).removeClass("active");

    });
}

function navbar_update(numero) {
    iter = 0;
    $("#navbar a").each(function () {
        if (iter === numero) {
            $(this).addClass("active");
        }
        iter++;
    });
}
