"""
Tutorial/Example how to use the class helper `SeriesHelper`
"""

from influxdb import InfluxDBClient
from influxdb import SeriesHelper
import time
# InfluxDB connections settings
host = '192.168.201.129'
port = 8086
user = 'root'
password = 'root'
dbname = 'prac'
t = time.time()
myclient = InfluxDBClient(host, port, user, password, dbname)

# Uncomment the following code if the database is not yet created
myclient.create_database(dbname)
#myclient.create_retention_policy('awesome_policy', '3d', 3, default=True)
def getfield():
    return ['some_stat1', 'other_stat1']
def gettags():
    return ['server_name1']

class MySeriesHelper(SeriesHelper):
    # Meta class stores time series helper configuration.
    class Meta:
        # The client should be an instance of InfluxDBClient.
        client = myclient
        # The series name must be a string. Add dependent fields/tags in curly brackets.
        series_name = 'eventsstats{server_name1}'
        # Defines all the fields in this time series.
        fields = getfield()
        # Defines all the tags for the series.
        tags = gettags()
        # Defines the number of data points to store prior to writing on the wire.
        bulk_size = 10
        # autocommit must be set to True when using bulk_size
        autocommit = False

# The following will create *five* (immutable) data points.
# Since bulk_size is set to 5, upon the fifth construction call, *all* data
# points will be written on the wire via MySeriesHelper.Meta.client.
MySeriesHelper(server_name1='useast1', some_stat1=159, other_stat1=10)
MySeriesHelper(server_name1='useast2', some_stat1=158, other_stat1=20)
MySeriesHelper(server_name1='useast3', some_stat1=157, other_stat1=30)
MySeriesHelper(server_name1='useast4', some_stat1=156, other_stat1=40)
MySeriesHelper(server_name1='useast5', some_stat1=12, other_stat1=50)
MySeriesHelper(server_name1='useast6', some_stat1=1, other_stat1=20)
MySeriesHelper(server_name1='useast7', some_stat1=2, other_stat1=30)
MySeriesHelper(server_name1='useast8', some_stat1=3, other_stat1=40)
MySeriesHelper(server_name1='useast9', some_stat1=4, other_stat1=50)
MySeriesHelper(server_name1='useast10', some_stat1=5, other_stat1=10)
MySeriesHelper(server_name1='useast11', some_stat1=6, other_stat1=20)
MySeriesHelper(server_name1='useast12', some_stat1=7, other_stat1=30)
MySeriesHelper(server_name1='useast13', some_stat1=8, other_stat1=40)
MySeriesHelper(server_name1='useast14', some_stat1=9, other_stat1=50)
MySeriesHelper(server_name1='useast15', some_stat1=10, other_stat1=10)
MySeriesHelper(server_name1='useast16', some_stat1=11, other_stat1=20)
MySeriesHelper(server_name1='useast17', some_stat1=12, other_stat1=30)
MySeriesHelper(server_name1='useast18', some_stat1=13, other_stat1=40)
MySeriesHelper(server_name1='useast19', some_stat1=14, other_stat1=50)
MySeriesHelper(server_name1='useast20', some_stat1=15, other_stat1=10)
MySeriesHelper(server_name1='useast21', some_stat1=16, other_stat1=20)
MySeriesHelper(server_name1='useast22', some_stat1=17, other_stat1=30)
MySeriesHelper(server_name1='useast23', some_stat1=18, other_stat1=40)
MySeriesHelper(server_name1='useast24', some_stat1=19, other_stat1=50)
MySeriesHelper(server_name1='useast25', some_stat1=20, other_stat1=10)
MySeriesHelper(server_name1='useast', some_stat1=21, other_stat1=20)
MySeriesHelper(server_name1='useast', some_stat1=22, other_stat1=30)
MySeriesHelper(server_name1='useast', some_stat1=23, other_stat1=40)
MySeriesHelper(server_name1='useast', some_stat1=24, other_stat1=50)
MySeriesHelper(server_name1='useast', some_stat1=26, other_stat1=10)
MySeriesHelper(server_name1='useast', some_stat1=27, other_stat1=20)
MySeriesHelper(server_name1='useast', some_stat1=222, other_stat1=30)
MySeriesHelper(server_name1='useast', some_stat1=111, other_stat1=40)
MySeriesHelper(server_name1='useast', some_stat1=1111, other_stat1=50)
MySeriesHelper(server_name1='useast', some_stat1=3542, other_stat1=10)
MySeriesHelper(server_name1='useast', some_stat1=543, other_stat1=20)
MySeriesHelper(server_name1='useast', some_stat1=2343, other_stat1=30)
MySeriesHelper(server_name1='useast', some_stat1=1234, other_stat1=40)
MySeriesHelper(server_name1='useast', some_stat1=234, other_stat1=50)

# To manually submit data points which are not yet written, call commit:
MySeriesHelper.commit()
print time.time()-t
# To inspect the JSON which will be written, call _json_body_():
MySeriesHelper._json_body_()