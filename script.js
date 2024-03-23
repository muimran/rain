


let map = L.map('map').setView([0,0], 1);


const fs = require('fs');
const csv = require('csv-parser');

const filename = "coordinates_rainfall_data.csv";

const existing_data = [];

fs.createReadStream(filename)
  .pipe(csv())
  .on('data', (row) => {
    existing_data.push(row);
  })
  .on('end', () => {
    console.log(existing_data); // Or do something else with the data
  });



var heat = L.heatLayer(existing_data).addTo(map);
