const chart = Highcharts.chart('container', {
    chart: {
        type: 'spline'
    },
    title: {
        text: null
    },
    sonification: {
        duration: 27000,
        afterSeriesWait: 1200,
        defaultInstrumentOptions: {
            instrument: 'basic2',
            mapping: {
                playDelay: 500
            }
        },
        // Speak the series name at beginning of series
        globalTracks: [{
            type: 'speech',
            mapping: {
                text: '{point.series.name}',
                volume: 0.4,
                rate: 2
            },
            // Active on first point in series only
            activeWhen: function (e) {
                return e.point && !e.point.index;
            }
        }]
    },
    accessibility: {
        screenReaderSection: {
            axisRangeDateFormat: '%B %Y',
            beforeChartFormat: ''
        },
        point: {
            dateFormat: '%b %e, %Y',
            valueDescriptionFormat: '{value}{separator}{xDescription}'
        },
        series: {
            pointDescriptionEnabledThreshold: false
        }
    },
    colors: ['#3d3f51', '#42858C', '#AD343E'],
    plotOptions: {
        series: {
            label: {
                connectorAllowed: true
            },
            marker: {
                enabled: false
            },
            cropThreshold: 10
        }
    },
    yAxis: {
        title: {
            text: null
        },
        accessibility: {
            description: 'Percent unemployment of labor force'
        },
        labels: {
            format: '{text}%'
        }
    },
    xAxis: {
        accessibility: {
            description: 'Time'
        },
        type: 'datetime'
    },
    tooltip: {
        valueSuffix: '%',
        stickOnContact: true
    },
    legend: {
        enabled: false
    }
});

// Fetch the CSV file from GitHub repository
fetch('https://raw.githubusercontent.com/your_username/your_repository/main/rainfall_data.csv')
    .then(response => response.text())
    .then(data => {
        // Load CSV data into chart
        chart.update({
            data: {
                csv: data
            }
        });
    })
    .catch(error => {
        console.error('Error fetching CSV file:', error);
    });

// Handle the keyboard navigation
// (Your existing keyboard navigation code remains unchanged)
