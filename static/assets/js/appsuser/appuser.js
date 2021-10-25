
$(document).ready(function () {


    let SendInfo = {

        };
    let oldemail=null;

        $.ajax({
            type: 'post',
            url: '/get_sysuser_info',
            data: JSON.stringify(SendInfo),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                oldemail = data.email
                $("#email").val(data.email);
            },
            error: function (xhr) {
                console.log(xhr)
                createAlert('Opps!', 'Something went wrong', xhr, 'danger', true, false, 'pageMessages');
            }
        });

    $("#btn_actualizar").click(function () {

        let password = $("#password").val();
        let email = $("#email").val();
        if (email!== undefined && email !== oldemail && email.length > 0  && password !== "nopassword") {
            updateEmail(email)
            updatePass(password)

        } else {
            if(email === oldemail && password === "nopassword"){
                 alert("Nada que modificar")
            }else
            if (email!== undefined && email.length > 0 && email !== oldemail) {
                updateEmail(email)

            }
            if (password !== "nopassword") {
                updatePass(password)
            }
        }
    });


    function updatePass(password) {
        let SendInfo = {
            new_password: password
        };

        $.ajax({
            type: 'post',
            url: '/change_password_sys_user',
            data: JSON.stringify(SendInfo),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {

                createAlert('Exito!', 'Se ha actualizado', 'La contraseña ha sido actualizado, se redirigira a la pantalla de login' , 'success', true, true, 'pageMessages');
                setTimeout(function () {
                    $(location).attr('href', '/');
                }, 5000);
            },
            error: function (xhr) {
                alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
            }
        });


    }

    function updateEmail(email) {
        let SendInfo = {
            new_email: email
        };

        $.ajax({
            type: 'post',
            url: '/change_email_sys_user',
            data: JSON.stringify(SendInfo),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                createAlert('Exito!', 'Se ha actualizado', 'El correo electronico ha sido actualizado, ahora recibiras las notificaciones a ' + email, 'success', true, true, 'pageMessages');
                setTimeout(function () {
                    $(location).attr('href', '/');
                }, 5000);

            },
            error: function (xhr) {
                createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
            }
        });

    }


});

