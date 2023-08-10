#!/home/betorcha/miniconda3/envs/geopandas_jupyter/bin/python
import os
from datetime import datetime
os.system('wget https://download.geofabrik.de/africa/algeria-latest.osm.pbf -O ~/Ml_projects/osm_data/data/algeria.osm.pbf')
os.system ('ogr2ogr -f SQLite -lco FORMAT=WKT ~/Ml_projects/Osm/data/algeria_osm.sqlite ~/Ml_projects/osm_data/data/algeria.osm.pbf')