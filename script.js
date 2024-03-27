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
                    dateTimeLabelFormats: {
                        month: '%e. %b',
                        year: '%b'
                    },
                    title: {
                        text: 'Date'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Rainfall (mm)'
                    }
                },
                tooltip: {
                    shared: true,
                    crosshairs: true
                },
                plotOptions: {
                    spline: {
                        marker: {
                            enabled: true
                        },
                        dataLabels: {
                            enabled: true
                        }
                    }
                },
                data: {
                    csv: csv,
                    parsed: function (columns) {
                        // Parse the datetime column to timestamps and convert numerical values
                        columns.forEach(function (column, i) {
                            if (i === 0) { // The first column is datetime
                                for (let j = 1; j < column.length; j++) {
                                    column[j] = Date.parse(column[j]);
                                }
                            } else { // Convert string numerical values to floats
                                for (let j = 1; j < column.length; j++) {
                                    column[j] = parseFloat(column[j]);
                                }
                            }
                        });
                    },
                    complete: function (options) {
                        // Filter the series by the specified column names
                        options.series = options.series.filter(series => {
                            return [
                                'Average Rainfall',
                                'Average England rainfall',
                                'average Scotland rainfall',
                                'average Wales rainfall',
                                'Total Rainfall',
                                'Total England rainfall',
                                'total Scotland rainfall',
                                'total Wales rainfall'
                            ].includes(series.name);
                        });
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading the CSV data: ', error);
        });
});
