let labels = []
let enviados = []
let recibidos = []
let bandera = false;


function getLogInfo() {
    $.ajax({
        type: 'post',
        url: '/log_get_all',
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (data) {
            console.log(data)
        },
        error: function (xhr) {
            console.log(xhr)
            createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
        }
    });
}


function myLoop(interface, router_name) {
    setTimeout(function () {
        $.ajax({
            type: 'post',
            url: '/get_sent_received_packets',
            contentType: "application/json; charset=utf-8",
            traditional: true,
            data: JSON.stringify({name: router_name, interface: interface}),
            success: function (data) {
                console.log(data);
                lineChartData.datasets[0].data.push();
                nuevosEnviados = data.sent - lineChartData.datasets[0].data[lineChartData.datasets[0].data.length - 1]
                nuevosRecibidos = data.received - lineChartData.datasets[1].data[lineChartData.datasets[1].data.length - 1]
                if (nuevosEnviados > 0) {
                    lineChartData.datasets[0].data.push(data.sent)
                } else {
                    lineChartData.datasets[0].data.push(0)
                }
                if (nuevosRecibidos > 0) {
                    lineChartData.datasets[1].data.push(data.received)
                } else {
                    lineChartData.datasets[1].data.push(0)
                }
                if (lineChartData.datasets[0].data.length > 5) {
                    lineChartData.datasets[0].data.shift()
                    lineChartData.datasets[1].data.shift()
                    lineChartData.labels.shift()
                }
                const d = new Date();
                let time = d.getTime();
                lineChartData.labels.push(time)
                window.myLine.update();
            },
            error: function (xhr) {
                console.log(xhr)
                createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
            }
        });

        if (bandera) {
            myLoop(interface, router_name);

        }
    }, 3000)
}


$(document).ready(function () {

    $('#select_router').on('change', function () {
        labels = []
        enviados = []
        recibidos = []
        bandera = false;
        if (this.value !== "-1") {
            $.ajax({
                type: 'post',
                url: '/search_router_con',
                contentType: "application/json; charset=utf-8",
                traditional: true,
                data: JSON.stringify({name: this.value}),
                success: function (data) {
                    //console.log(data.conns);
                    let conns = data.conns
                    let html = "<option value=\"-1\" selected>Seleccione una interfaz</option>";
                    for (let j = 0; j < conns.length; j++) {
                        html = html + '<option value="' + conns[j].interface + '">' + conns[j].interface + '</option>'
                    }
                    $("#interfaces").html(html);
                },
                error: function (xhr) {
                    console.log(xhr)
                    createAlert('Opps!', 'Something went wrong', 'Here is a bunch of text about some stuff that happened.', 'danger', true, false, 'pageMessages');
                }
            });
        } else {
            let html = "<option value=\"-1\" selected>Seleccione una interfaz</option>";
            $("#interfaces").html(html);
        }
    });
    $('#interfaces').on('change', function () {
        if (this.value !== "-1") {
            bandera = true;
            myLoop(this.value, $("#select_router").val());
        } else {
            bandera = false;
        }
    });
    getLogInfo();
    /*const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Usuarios', 'Routers', 'Usuarios de router'],
            datasets: [{
                data: [len_users, len_routers, len_router_users],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });*/
});


var lineChartData = {
    labels: labels,
    datasets: [{
        label: "Enviados",
        borderColor: window.chartColors.red,
        backgroundColor: window.chartColors.red,
        fill: false,
        data: enviados,
        yAxisID: "y-axis-1",
    }, {
        label: "Recibidos",
        borderColor: window.chartColors.blue,
        backgroundColor: window.chartColors.blue,
        fill: false,
        data: recibidos,
        yAxisID: "y-axis-2"
    }]
};

window.onload = function () {
    var ctx = document.getElementById("myChart").getContext("2d");
    window.myLine = Chart.Line(ctx, {
        data: lineChartData,
        options: {
            responsive: true,
            hoverMode: 'index',
            stacked: false,
            title: {
                display: true,
                text: 'Paquetes recibidos y enviados'
            },
            scales: {
                yAxes: [{
                    type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: "left",
                    id: "y-axis-1",
                }, {
                    type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: "right",
                    id: "y-axis-2",

                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }],
            }
        }
    });
};

/*document.getElementById('randomizeData').addEventListener('click', function () {
    lineChartData.datasets.forEach(function (dataset) {
        dataset.data = dataset.data.map(function () {
            return randomScalingFactor();
        });
    });

    window.myLine.update();
});*/
