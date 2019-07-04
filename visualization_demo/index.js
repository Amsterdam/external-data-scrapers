var yesterday = new Date()
// Always start with yesterday since summaries are done overnight.
yesterday.setDate(yesterday.getDate() - 1);
//var yesterday = new Date(Date.UTC(2019, 4, 23, 3, 0, 0))

day = ("0" + yesterday.getDate()).slice(-2); 
month = ("0" + (yesterday.getMonth() + 1)).slice(-2); // Months start at 0 because JavaScript.
year = yesterday.getFullYear()

rootURL = 'https://acc.map.data.amsterdam.nl'
currentDate = `${year}-${month}-${day}`
currentBucket = "3"
currentSign = "A1"
//rootURL = 'http://localhost:8070' // Local

const trafficSigns = ["A1","A2","A3","A4","A5","B1","B2","B3","B4","B5","B6","B7","C1","C10","C11","C12","C13","C14","C15","C16","C17","C18","C19","C2","C20","C21","C22a","C3","C4","C5","C6","C7","C7a","C7b","C8","C9","D1","D2","D3","D4","D5","D6","D7","E1","E10","E11","E12","E13","E2","E3","E4","E5","E6","E7","E8","E9","F1","F13","F14","F15","F17","F19","F21","F3","F5","F6","F7","F8","F9","G1","G10","G11","G12","G12a","G12b","G13","G14","G2","G3","G4","G5","G6","G7","G8","G9","H1","H2","J14","J15","J16","J17","J18","J19","J2","J21","J22","J23","J24","J29","J3","J32","J37","J38","J39","J5","J8","J9","K14","K4","L1","L10","L11","L12","L14","L2","L20","L3","L4","L5","L6","L8","L9","N.v.t.","WM1","WM10","WM11","WM12","WM2","WM3","WM4","WM5","WM6","WM7","WM8","WM9"]

const url = 'http://localhost:8070/maps/verkeerbesluiten?Typename=verkeerbesluiten&REQUEST=GetFeature&SERVICE=wfs&OUTPUTFORMAT=application/json;%20subtype=geojson;%20charset=utf-8&version=1.1.0&srsname=urn:ogc:def:crs:EPSG::4326';

const fetchRequest = (bbox_str) => fetch(`${url}&bbox=${bbox_str}&trafficsign=${currentSign}`)
        .then(response => response.json())
        .then(json => {
            console.log('received: ', json); // eslint-disable-line no-console
            return json;
        })

const bboxLayerOptions = {
    fetchRequest,
};

const geojsonLayerOptions = {
    zoomMin: 14,

    pointToLayer(feature, latlng) {
        let traffic_sign = feature.properties.traffic_sign_code
        let feature_link = `https://zoek.officielebekendmakingen.nl/${traffic_sign}.html`
        let icon = L.divIcon({html: `<img alt=" " src="traffic_signs/${traffic_sign}.svg" width="20" height="20"<p>${traffic_sign}</p>`, iconSize: [16, 16], className: 'divIcon green'});
        let marker = L.marker(latlng, {icon: icon});
        marker.bindPopup(`
        <ul>
          <li><b>Title</b>: ${feature.properties.title}</li>
          <li><b>Identifier</b>: <a href="${feature_link}">${feature.properties.identifier}</a></li>
          <li><b>Traffic sign</b>: ${feature.properties.traffic_sign_code}</li>
          <li><b>Creator</b>: ${feature.properties.creator}</li>
          <li><b>Available</b>: ${feature.properties.available}</li>
        </ul>`);
        return marker
    },

};

BOUNDING_BOX = {
    COORDINATES: {
        southWest: [52.25168, 4.64034],
        northEast: [52.50536, 5.10737]
    }
};

BOUNDS = [
            BOUNDING_BOX.COORDINATES.southWest,
            BOUNDING_BOX.COORDINATES.northEast
        ];

var mymap = L.map('mapid').setView([52.381120, 4.882912], 14);

L.tileLayer('https://acc.{s}.data.amsterdam.nl/{id}/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://data.amsterdam.nl">City Data</a>, Amsterdam City Data',
    minZoom: 7,
    maxZoom: 18,
    id: 'topo_wm_zw',
    // id: 'topo_rd',
    // crs: L.CRS.RD,
    maxBounds: BOUNDS,
    subdomains: ['t1', 't2', 't3', 't4']
}).addTo(mymap)

wmsServices = {
    "NDW Traveltime": L.tileLayer.wms(rootURL + '/maps/traveltime?REQUEST=GetCapabilities&VERSION=1.1.0&SERVICE=wms', {
          layers: ['traveltime_by_day'],
          date: currentDate,
          bucket: currentBucket,
          transparent: true,
          format: 'image/png',
          isBaseLayer: false,
          tiled: true,
          maxBounds: BOUNDS,
          crs: L.CRS.RD
          }),

    "OV Traveltime": L.tileLayer.wms(rootURL + '/maps/ovtramstraveltime?REQUEST=GetCapabilities&VERSION=1.1.0&SERVICE=wms', {
          layers: ['ovtramstraveltime_by_day'],
          date: currentDate,
          bucket: currentBucket,
          transparent: true,
          format: 'image/png',
          isBaseLayer: false,
          tiled: true,
          maxBounds: BOUNDS,
          crs: L.CRS.RD
          }),

    "Traffic signs": geojsonBboxLayer(bboxLayerOptions, geojsonLayerOptions)
}

L.control.layers(wmsServices).addTo(mymap);

var ndwLegend = L.control({position: 'bottomright'});
var ovLegend = L.control({position: 'bottomright'});

ndwLegend.onAdd = function (mymap) {
    var div = L.DomUtil.create('div', 'info legend')
    imageURL = rootURL + "/cgi-bin/mapserv?map=/srv/mapserver/traveltime.map&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=latest_traveltime&format=image/png&STYLE=default&"
    div.innerHTML += `<img src="${imageURL}"/>`
    return div;
};

ovLegend.onAdd = function (mymap) {
    var div = L.DomUtil.create('div', 'info legend')
    imageURL = rootURL + "/cgi-bin/mapserv?map=/srv/mapserver/ovtramstraveltime.map&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=ovtramstraveltime_by_day&format=image/png&STYLE=default"
    div.innerHTML += `<img src="${imageURL}"/>`
    return div;
};


let isTrafficSigns = (service) => {
    if (service == "Traffic signs") {
        return true 
    }
    return false
};
change_bucket = function(value){
    for (service in wmsServices) {
        if (isTrafficSigns(service)){
        wmsServices[service].setParams({bucket: value})
        }
    }
    currentBucket = value
};

change_date = function(value){
    for (service in wmsServices) {
        if (isTrafficSigns(service)){
        wmsServices[service].setParams({date: value})
        }
    }
    currentDate = value
};

let change_sign = (value) => {
    currentSign = value;
    wmsServices["Traffic signs"]._fetchNewData()
};

var wmsControl = L.control({position: 'topright'});

wmsControl.onAdd = function(mymap){
    var div = L.DomUtil.create('div', 'info')
    div.innerHTML += `
    <form>
      <div>
          <input type="date" id="dateInput"> 
      </div>

      <div>
        <label>
        <input type="radio" id="bucket1"
         name="bucket" onClick="change_bucket(1)">
         Morning rush-hour</label>
      </div>

      <div>
        <label>
        <input type="radio" id="bucket2"
         name="bucket" onClick="change_bucket(2)">
         Evening rush-hour</label>
      </div>

      <div>
        <label>
        <input type="radio" id="bucket3"
         name="bucket" onClick="change_bucket(3)">
         Rest of the day</label>
      </div>
    </form>`;
    return div
};

var trafficSignControl = L.control({position: 'topright'});

trafficSignControl.onAdd = function(mymap){
    var div = L.DomUtil.create('div', 'signs')
    div.innerHTML += "<form>";

    for (let sign of trafficSigns) {
        div.innerHTML += `
        <div>
          <label>
          <input type="radio" name="trafficsigns" id="${sign}" onClick="change_sign('${sign}')">
          ${sign}</label>
        </div>`;
    }
    div.innerHTML += "</form>";
    return div
};

let setDefaultwmsControl = () => {
    document.getElementById("bucket"+currentBucket).checked = true; // set to current bucket
    document.getElementById("dateInput").value = currentDate; // set to current date
}
mymap.on('layeradd', function (eventLayer) {
        this.removeControl(ndwLegend);
        this.removeControl(ovLegend);
        this.removeControl(wmsControl);
        this.removeControl(trafficSignControl)

    if (mymap.hasLayer(wmsServices["Traffic signs"])){
        trafficSignControl.addTo(this);
        document.getElementById(currentSign).checked = true; // set to current bucket
    }
    else if (mymap.hasLayer(wmsServices["OV Traveltime"])) {
        ovLegend.addTo(this);
        wmsControl.addTo(this);
        setDefaultwmsControl();
    } else { 
        ndwLegend.addTo(this);
        wmsControl.addTo(this);
        setDefaultwmsControl();
    }
});

wmsServices["NDW Traveltime"].addTo(mymap);
ndwLegend.addTo(mymap);
wmsControl.addTo(mymap);

setDefaultwmsControl()
document.getElementById("dateInput").addEventListener("change", function() {
    change_date(this.value)
});
