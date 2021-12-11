document.addEventListener('DOMContentLoaded', function () {
    dibujarRed();

})

function dibujarRed() {

    $.ajax({
            type: 'post',
            url: '/get_topology',
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                console.log(data);
                cytoscapePintar(data);
            },
            error: function (xhr) {
                if (xhr.responseText === "Invalid_Credentials") {
                    createAlert('Opps!', 'Something went wrong', xhr.responseText, 'danger', true, true, 'pageMessages');
                } else {
                    createAlert('Opps!', 'Something went wrong', 'please contact system support assistance', 'danger', true, true, 'pageMessages');

                }

//                alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
            }
        });





}


function cytoscapePintar(data){
    cytoscape({
        container: document.getElementById('cy'),

        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(id)',
                    'background-color': '#e27846',
                }
            },

            {
                selector: 'edge',
                style: {
                    'target-label': function (edge) {
                        return ((edge.data().label).split("-")[0] + "\n\n \u2060")
                    },
                    'source-label':function (edge) {
                        return ((edge.data().label).split("-")[1] + "\n\n \u2060")
                    },
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'source-arrow-shape': 'triangle',
                    'text-wrap': 'wrap',
                    'source-text-rotation': 'autorotate',
                    'target-text-rotation': 'autorotate',
                    'line-color': '#013289',
                    'target-arrow-color': '#013289',
                    'source-arrow-color': '#013289',
                }
            }
        ],

        elements: data,

        layout: {
            name: 'grid'
        }
    });
}