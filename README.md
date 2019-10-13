# checkpointPlus Final
This version uses speedtest-cli to run the tests instead of iPerf.

The program takes a list of ookla servers (using their id numbers) and then cycles thru them running both a multi-threaded test and a single threaded test.

It then selects the highest value from the Download results and presents that to the user.

# Result retention

Once completed, all results are sent to checkpointdb_version4 database.

The database should reside in a docker for isolation and rapid restoration in the event of a failure.  However, the code does allow for a failure to occur on the upload of the results.  In the event of such a failure, the results are lost (as they are not retained locally).

# Creating database

Use the following commands to create the docker container:

```
docker container run --name checkpointdb_version4 -d -e MYSQL_ROOT_PASSWORD=titpfcheckpoint! -p 3310:3306 -v $(pwd)/ -d mariadb
```

access the container:
```
docker exec -it checkpointdb_version4 bash
```

then create the database:
```
mysql -u root -p
create database checkpointdb_version4
```

then the tables:
```
use checkpointdb_version4



create table results (testID INT,identity varchar(20), wanip varchar(16), lanip varchar(16), multithread_down int(16), multithread_up float(16), multithread_target int(11),multithread_latency float, multithread_sponsor varchar(100), multithread_share varchar(200), singlethread_down float(16),singlethread_up float(16), singlethread_target int(11), singelthread_latency float, singlethread_sponsor varchar(100), singlethread_share varchar(200),timeCreate timestamp); 
```

# REQUIREMENTS

This code uses the speedtest-cli script written by sivel.  Install this on the Pi:

```
mkdir speedtest-cli
cd speedtest-cli
curl -Lo speedtest-cli https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
chmod +x speedtest-cli
speedtest-cli
```

add the directory to your PATH. On the dietpi:

```
PATH=$PATH:/root/speedtest-cli-code/
```
