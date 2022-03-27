"""
Loads bikeshare data from the landing/ directory, flattens it out and writes it to output/ (caution: it will overwrite
  everything in the output/ folder).

Copyright (C) 2022 David Vas
See LICENSE file for more details.
"""

import logging
import os
import time

import pyspark
from config import Config
from bs_logger import BSLogger
from pyspark.sql import SparkSession
from template_parser import TemplateParser
from pyspark.sql.types import BooleanType
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry import Point
from shapely import wkt
from pyspark.sql.functions import date_format, udf, date_trunc, to_date

logger = BSLogger('load_bikeshare_data').get_logger()
BASE_PATH = os.path.join(os.path.dirname(__file__), '..')


def setup_spark(memory: str) -> pyspark.sql.session:
    session = SparkSession.builder\
                          .appName("load_bikeshare_data")\
                          .config("spark.jars.packages", "org.apache.spark:spark-avro_2.12:3.2.1") \
                          .config("spark.driver.memory", memory)\
                          .getOrCreate()
    # Setting up more complicated logging for Spark from within Pyton is incredibly hacky, and does not matter
    # for local executions. For managed Spark instances it's usually handled for us, but should be set via
    # log4j.properties if not, not here.
    session.sparkContext.setLogLevel('ERROR')  # running Spark locally has tons of warnings that can be ignored
    return session


def read_csv(spark_session, table_name):
    return spark_session.read.format("csv")\
                        .option("header", True)\
                        .load(os.path.join(BASE_PATH, f'landing/{table_name}'))


def read_avro(spark_session, table_name):
    return spark_session.read.format("avro")\
                        .option("compression", "snappy")\
                        .load(os.path.join(BASE_PATH, f'landing/{table_name}'))


def point_in_multipoly(point, multi_poly) -> bool:
    if multi_poly == "" or point == "POINT EMPTY" or multi_poly == "MULTIPOLYGON EMPTY" or point == "" \
            or point is None or multi_poly is None:
        return False
    try:
        mp = MultiPolygon(wkt.loads(str(multi_poly)))
        point = Point(wkt.loads(str(point)))
        if mp.contains(point):
            return True
        else:
            return False
    except:
        return False


point_in_mp_udf = udf(lambda x, y: point_in_multipoly(x, y), BooleanType())


def unionall_dfs(spark_session: pyspark.sql.session, table_list: list, input_format: str):
    if input_format == 'avro':
        read_func = read_avro
    elif input_format == 'csv':
        read_func = read_csv
    else:
        return None
    tl = table_list.copy()
    t1 = tl.pop(0)
    logger.info(f"Loading data from {t1}")
    df = read_func(spark_session, t1)
    for table in tl:
        logger.info(f"Loading data from {table} and appending to previous DF")
        df = df.unionAll(read_func(spark_session, t1))
    return df


if __name__ == "__main__":
    config = Config(BASE_PATH, os.path.join(BASE_PATH, 'config/config.yaml')).get_config()['build_config']['load_sfo_data']
    parser = TemplateParser(config)
    logger.debug(parser.render("This should look unlike a template: {{baseloc}}"))
    spark = setup_spark(config['memory'])
    trips = unionall_dfs(spark, config['trips'], 'avro')\
        .select(date_format('start_date', 'yyyy-MM').alias('date_partition'),  #usually I'd go with daily partitions, but this is a small-ish dataset so I wouldn't want to blow the filesystem up
                date_trunc('Day', 'start_date').alias('start_date_day'),
                '*')\
        .drop('start_station_name',
              'end_station_name',
              'start_station_latitude',
              'end_station_latitude',
              'start_station_longitude',
              'end_station_longitude',
              'start_station_geom',
              'end_station_geom')  # these columns will come from the stations table
    stations = unionall_dfs(spark, config['stations'], 'avro')
    zipcodes = unionall_dfs(spark, config['zipcodes'], 'csv')
    weather = unionall_dfs(spark, config['weather'], 'csv')\
        .select(to_date('PDT', 'M/d/yyyy').alias('weather_date'), '*')\
        .drop('PDT')
    for column in weather.columns:
        weather = weather.withColumnRenamed(column, column.replace(' ', '_'))  # whitespace is not avro's favorite
    logger.info("Joining stations to zipcodes (spatial)")
    joined_special_spatial = stations.join(zipcodes, point_in_mp_udf(stations.station_geom, zipcodes.the_geom))\
                                     .select(stations.station_id.alias('zip_station_id'), zipcodes.zip)
    logger.info("Joining back to stations")
    stations_projection = stations.columns + ['zip']
    # this extra join is needed as outer joins are not supported with UDFs:
    panic_station = stations.join(joined_special_spatial, stations.station_id == joined_special_spatial.zip_station_id,
                                  'left_outer')\
                            .select(*stations_projection)
    logger.info("Producing final dataset")

    def prefixer(item, prefix):
        return f"{item} AS {prefix}_station_{item}" if not item.startswith("station_") else f"{item} AS {prefix}_{item}"

    def start_prefixer(item): return prefixer(item, "start")
    def end_prefixer(item): return prefixer(item, "end")
    start_station_projection = map(start_prefixer, panic_station.columns)
    end_station_projection = map(end_prefixer, panic_station.columns)
    start_stations = panic_station.selectExpr(*start_station_projection)
    end_stations = panic_station.selectExpr(*end_station_projection)

    # makes dot your favorite character not just in regex golf
    trips.join(start_stations, trips.start_station_id == start_stations.start_station_id, 'left_outer')\
         .join(end_stations, trips.end_station_id == end_stations.end_station_id, 'left_outer')\
         .join(weather, [start_stations.start_station_zip == weather.ZIP,
                         trips.start_date_day == weather.weather_date], 'left_outer')\
         .drop('start_station_id', 'end_station_id', 'weather_date', 'ZIP')\
         .write.mode('overwrite')\
         .partitionBy('date_partition')\
         .format('avro').option('compression', 'snappy')\
         .save(config['output'])

    logger.info("Finished processing of bikeshare data")