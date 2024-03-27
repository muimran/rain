document.addEventListener('DOMContentLoaded', function () {
    fetch('rainfall_data.csv')
        .then(response => response.text())
        .then(csv => {
            Highcharts.chart('container', {
                chart: {
                    type: 'spline'
                },
                title: {
                    text: 'Rainfall Data Over Time'
                },
                subtitle: {
                    text: 'Average and Total Rainfall for England, Scotland, and Wales'
                },
                xAxis: {
                    type: 'datetime',
                    accessibility: {
                        description: 'Time'
                    },
                    dateTimeLabelFormats: { // don't display the dummy year
                        month: '%e. %b',
                        year: '%b'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Rainfall (mm)'
                    },
                    labels: {
                        format: '{value} mm'
                    }
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: '{point.x:%e. %b}: {point.y:.2f} mm'
                },
                plotOptions: {
                    spline: {
                        marker: {
                            enabled: true
                        }
                    }
                },
                data: {
                    csv: csv,
                    parsed: function (columns) {
                        // Parse the datetime column to make it a valid Date for Highcharts
                        columns[0].forEach(function (v, i) {
                            columns[0][i] = Date.parse(v);
                        });
                    }
                }
                // Note: If you want to add sonification and accessibility features,
                // include the configurations here as in your previous example.
            });
        })
        .catch(error => {
            console.error('Error loading the CSV data: ', error);
        });
});
