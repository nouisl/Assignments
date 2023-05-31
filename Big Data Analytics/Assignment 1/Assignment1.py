# Noushin Islam (Student no. 201508438)
# Assignment 1 - COMP336

# To run the code locally use: spark-submit --master local[1] PART-1.py
# make sure to open your terminal in the directory with this file saved on it when running it

# importing pyspark libraries and functions
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql.window import Window

# change this string to the path of the txt/csv file used if run on a different machine   
dataset = 'dataset.txt'

# building SparkSession locally
spark = SparkSession.builder.master('local[1]').appName('PART-1').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

# importing dataset and casting data
df = spark.read.option('header',True).option('delimiter', ',').csv(dataset)
df = df.withColumn('UserID', df.UserID.cast(IntegerType()))\
     .withColumn('Latitude', df.Latitude.cast(DoubleType()))\
     .withColumn('Longitude', df.Longitude.cast(DoubleType()))\
     .withColumn('Altitude', df.Altitude.cast(DoubleType()))\
     .withColumn('Timestamp', df.Timestamp.cast(DoubleType()))\
     .withColumn('Date', df.Date.cast(DateType()))

# 1
print('\nTask 1')
# adding 5.5 hours to Timestamp, Date and Time in all data points

# first combine date and time to DateTime and convert it to timestamp format to add time
dt = df.withColumn('DateTime', concat_ws(' ', col('Date'), col('Time')))
task1 = dt.withColumn('DateTime', to_timestamp('DateTime') + expr('INTERVAL 5 HOURS 30 MINUTES'))
# add the same time to the column named Timestamp
# then extract data and time from DateTime and drop DateTime 
task1 = task1.withColumn('Timestamp', col('Timestamp')+(5.5/24))\
        .withColumn('Date', to_timestamp('DateTime').cast('date'))\
        .withColumn('Time', date_format('DateTime', 'HH:mm:ss'))\
        .drop('DateTime')

# uncomment following line to show top 20 rows
# task1.show()

# from here on I will be using the data processed in task 1

# 2
print('\nTask 2')
# calculating for each UserID on how many days the data was recorded at least twice and displaying top 10

# group by UserID, Date and count the data points
task2 = task1.groupBy('UserID', 'Date').count().withColumnRenamed('count', 'data points')
# filter the results to drop any rows with less than than two data points
task2 = task2.filter(col('data points') >= 2).drop('count')
# group by UserID and count the days and sort data
task2 = task2.groupBy('UserID').count().withColumnRenamed('count', 'number of days')\
        .orderBy(col('number of days').desc(), col('UserID').desc())

# output of top 10 users
task2.show(10)
 
# 3
print('\nTask 3')
# calculating for each UserID on how many days the data was recorded at least 150 times and displaying 

# group by UserID, Date and count the data points
task3 = task1.groupBy('UserID','Date').count().withColumnRenamed('count', 'data points')
# filter the results to drop any rows with less than than 150 data points
task3 = task3.filter(col('data points') > 150).drop('count')
# group by UserID and count the days and sort data
task3 = task3.groupBy('UserID').count().withColumnRenamed('count', 'number of days')\
        .orderBy(col('number of days').desc(), col('UserID').desc())

# output all users
task3.show(task3.count())

# 4
print('\nTask 4')
# finding for each UserID the most northern part they reached and displaying top 10

# group by UserID and find max Latitude for each user
task4 = task1.groupBy('UserID').agg(max('Latitude').alias('Latitude'))
# find the corresponding date using .join
# group by UserID and Latitude and choose latest date and sort data
task4 = task4.join(task1, on=['UserID', 'Latitude'], how='inner')\
        .groupBy('UserID', 'Latitude').agg(max('Date').alias('Date'))\
        .orderBy(col('Latitude').desc(), col('Date').desc(), col('UserID').desc())

# output of top 10 users
task4.show(10)

# 5
print('\nTask 5')
#calculating for each UserID the difference between highest and lowest altitude reached and displaying top 10

# group by UserID and find max and min Altitude 
task5 = task1.groupBy('UserID').agg(max('Altitude').alias('maxAltitude'), min('Altitude').alias('minAltitude'))
# calculate the difference between the two values and sort data
task5 = task5.withColumn('Difference', col('maxAltitude') - col('minAltitude'))\
        .select(col('UserID'), col('Difference')).orderBy(col('Difference').desc(),col('UserID').desc())

# output of top 10 users
task5.show(10)

# 6
print('\nTask 6')
#calculating for each UserID the sum of the daily and total heights climbed
 
# select column and sort them
task6 = task1.select(col('UserID'), col('Date'), col('Timestamp'), col('Altitude'))\
        .orderBy(col('UserID').desc(), col('Timestamp').asc())
# partition by UserID and sort by Timestamp
w = Window.partitionBy('UserID').orderBy(col('Timestamp').asc())
# lag the position and calculate the altitude difference
l = task6.withColumn('prevA', lag('Altitude').over(w))
dist = l.withColumn('height', col('Altitude') - col('prevA'))
# filter the result to get rid of non-positive values
 # group by UserID and Date and sum the height for each user and sort data
task6 = dist.filter(col('height') > 0).groupBy('UserID', 'Date').sum('height')\
        .drop('TimeStamp', 'prevA').orderBy(col('sum(height)').desc(), col('Date').desc())
# partition by UserID and sort data
w_2 = Window.partitionBy('UserID').orderBy(col('sum(height)').desc(), col('Date').desc()) 
# get the latest day day each user climbed the most
task6_1 = task6.withColumn('row', row_number().over(w_2)).filter(col('row') == 1)\
          .drop('row').withColumnRenamed('sum(height)', 'max height')\
          .orderBy(col('max height').desc(), col('UserID').desc())
# sum all the height values to get the total value
task6_2 = task6.select(sum('sum(height)')).withColumn('Total height climbed', col('sum(sum(height))'))\
          .drop('sum(sum(height))')

# output all users
task6_1.show(task6_1.count())
print('\n')
# output all
task6_2.show(task6_2.count())
