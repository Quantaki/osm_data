#!/home/betorcha/miniconda3/envs/geopandas_jupyter/bin/python
import gc
import pandas as pd
import geopandas as gpd
import sqlite3
from shapely import wkt
from shapely import make_valid
from shapely.errors import GEOSException



def size_sqlite_table(table_name, con) : 
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    results = cursor.fetchall()
    size = len(results)
    del cursor
    _ = gc.collect()
    return size

def gpd_osm_within_wilaya(osm_table_name, wilaya, chunks = 2) : 
    
    # Create connexion with db
    sql_con_wilayats = sqlite3.connect("/home/betorcha/Ml_projects/osm_data/data/dz_decoupage.db")
    sql_con_osm = sqlite3.connect("/home/betorcha/Ml_projects/osm_data/data/algeria_osm.sqlite")

    # first get the size of table
    table_size = size_sqlite_table(osm_table_name, sql_con_osm)
    print(f"Size of table {osm_table_name} : {table_size}")

    # filter wilaya of interest
    dz = pd.read_sql('select * from all_wilayas;', con = sql_con_wilayats)
    w_geom = dz.loc[dz['name'] == wilaya, 'WKT_GEOMETRY']
    w_geom = wkt.loads(w_geom.values[0])

    # Load chunk of data (virtual memory efficciency)
    
    lim = int(table_size/chunks)
    off = 0
    data = []

    for chunk in range(chunks) : 
        
        df = pd.read_sql(f'select * from {osm_table_name} limit {lim} OFFSET {off};', sql_con_osm)
        #print('df shape', df.shape)

        # is in w_geom?
        geoser = gpd.GeoSeries.from_wkt(df['WKT_GEOMETRY'])
        
        try : 
            mask_w = geoser.within(w_geom)
        except GEOSException as e : 
            print("GEOSException handled : make_valid geometry is ongoing..")
            geoser = geoser.apply(lambda geom: make_valid(geom) if not geom.is_valid else geom)
            print("make_valid geometry completed")
            mask_w = geoser.within(w_geom)

        # keep df of wilaya of interest
        df = df[mask_w]
        data.append(df)

        off += int(table_size/chunks)

        if chunk == chunks-2 : 
            lim = table_size - int(table_size/chunks) * (chunks -1) 
        
        print(f"Chunk {chunk} successfuly loaded")

    # convert dataframe into geodataframe
    data = pd.concat(data, axis= 0, ignore_index = True)
    #data['geometry'] = gpd.GeoSeries.from_wkt(data['WKT_GEOMETRY'])
    #data = data.drop('WKT_GEOMETRY', axis = 1)
    #gdf = gpd.GeoDataFrame(data, geometry='geometry')
    #gdf.crs = 4326
#
    #del data, df, geoser, mask_w
    #_ = gc.collect()
    #
    #print(f"geopandas for {wilaya} of shape {gdf.shape} : operation completed!")

    return data


wilayats = ['Djelfa', 'Algiers', 'Blida']
tables = ['lines', 'points', 'multilinestrings', 'multipolygons', 'other_relations']


if __name__ == '__main__' :
        
    for wilaya in wilayats : 
        print('-' *5, f'{wilaya}', '-' *5)
        df_wilaya = []

        for osm_table_name  in tables : 

            df = gpd_osm_within_wilaya(osm_table_name, wilaya)
            df_wilaya.append(df)
        
        df_wilaya = pd.concat(df_wilaya, ignore_index=True)
        conn = sqlite3.connect(f'/home/betorcha/Ml_projects/osm_data/osm_wilayats_sqlite/osm_{wilaya}.db')
        df_wilaya.to_sql(f'osm_{wilaya}', conn, if_exists = 'replace', index = False)
        print(f'osm {wilaya} data succesfuly saved!')

        del df_wilaya, df, conn
        _ = gc.collect()
