## About NDW (Nationale Databank Wegverkeersgegevens)
NDW is a datasource that contains traffic data (for more info check: https://www.ndw.nu/en/)

We are currently scraping traveltime and trafficspeed data. The duration cars took to go through specific routes around the Netherlands. 

##Traveltime: 

Amount of time cars take to pass through certain routes in the Netherlands.
http://opendata.ndw.nu/traveltime.xml.gz The official NDW api.

##Trafficspeed: 

Speed and flow of vehicles at certain measurement points in the Netherlands
http://opendata.ndw.nu/trafficspeed.xml.gz The official NDW api.



###The following applies to both sources:
- Raw data is saved as is for history persistency
- Shapefile routes are imported on the fly and are supplied with stadsdeel and buurt codes.
- Raw data is cleaned and attached with the routes.
- Django REST api views the cleaned data.
- Django model needs to be in sync with the imported model
