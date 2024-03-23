mapboxgl.accessToken = 'pk.eyJ1IjoiZG93ZWxsYWYiLCJhIjoiY2x0cjJjc2VqMGVtZzJrbnYwZjcxczdkcCJ9.ljRbHHEIuM4J40yUamM8zg';
const map = new mapboxgl.Map({
    container: 'map', // container ID
    style: 'mapbox://styles/dowellaf/cltr2h0h0007y01p7akad96el', // style URL
    center: [0, 0], // starting position
    zoom: 1 // starting zoom
});




let geojsonData;

function updateAverageRainfall() {
    if (!geojsonData) return;

    let bounds = map.getBounds();
    let visibleFeatures = geojsonData.features.filter(feature => {
        let [lng, lat] = feature.geometry.coordinates;
        return bounds.contains([lng, lat]);
    });

    let totalRainfall = visibleFeatures.reduce((sum, feature) => {
        let rainfall = parseFloat(feature.properties.rainfall);
        return isNaN(rainfall) ? sum : sum + rainfall;
    }, 0);

    let averageRainfall = (visibleFeatures.length > 0) ? (totalRainfall / visibleFeatures.length).toFixed(2) : 'N/A';
    document.getElementById('info').textContent = 'Average Rainfall: ' + averageRainfall + ' mm';
}

map.on('load', () => {
    // Fetch GeoJSON data
    fetch('https://raw.githubusercontent.com/annadowell/soundbath_live_anna/imran/data/myData.geojson')
        .then(response => response.json())
        .then(data => {
            geojsonData = data;

            // Add a geojson point source for the rainfall data
            map.addSource('rainfall-data', {
                'type': 'geojson',
                'data': geojsonData
            });

            // Heatmap layer
            map.addLayer({
                'id': 'rainfall-heat',
                'type': 'heatmap',
                'source': 'rainfall-data',
                'maxzoom': 9,
                'paint': {
                    'heatmap-weight': [
                        'interpolate',
                        ['linear'],
                        ['to-number', ['get', 'rainfall'], 0],
                        0,
                        0,
                        1,
                        1
                    ],
                    'heatmap-intensity': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        0,
                        1,
                        9,
                        3
                    ],
                    'heatmap-color': [
                        'interpolate',
                        ['linear'],
                        ['heatmap-density'],
                        0,
                        'rgba(33,102,172,0)',
                        0.2,
                        'rgba(172, 159, 219, 0.8)',
                        0.4,
                        'rgba(142, 120, 217, 0.8)',
                        0.6,
                        'rgba(116, 86, 218, 0.8)',
                        0.8,
                        'rgba(92, 56, 214, 0.8)',
                        1,
                        'rgba(48, 0, 208, 0.8)'
                    ],
                    'heatmap-radius': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        0,
                        2,
                        10,
                        30,
                        14,
                        80
                    ],
                    'heatmap-opacity': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        7,
                        1,
                        10,
                        1,
                        14,
                        0
                    ]
                }
            }, 'waterway-label');


            // Circle layer to represent individual points
        map.addLayer({
          'id': 'rainfall-point',
          'type': 'circle',
          'source': 'rainfall-data',
          'minzoom': 7,
          'paint': {
              // Circle radius based on rainfall value
              'circle-radius': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  7,
                  ['interpolate', ['linear'], ['to-number', ['get', 'rainfall'], 0], 0, 1, 10, 10],
                  16,
                  ['interpolate', ['linear'], ['to-number', ['get', 'rainfall'], 0], 0, 5, 10, 50]
              ],
              // Circle color based on rainfall value
              'circle-color': [
                  'interpolate',
                  ['linear'],
                  ['to-number', ['get', 'rainfall'], 0],
                  0,
                  'rgba(33,102,172,0)',
                  .8,
                  'rgb(103,169,207)',
                  3,
                  'rgb(178,24,43)'
              ],
              'circle-stroke-color': 'white',
              'circle-stroke-width': 1,
              // Circle opacity adjustment based on zoom level
              'circle-opacity': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  8,
                  1,
                  22,
                  1
              ]
          }
      }, 'waterway-label');

            // Initialize and update the average calculation
            updateAverageRainfall();
        });

    // Update the average rainfall when the map is moved
    map.on('moveend', updateAverageRainfall);
});
