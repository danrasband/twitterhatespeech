#!/bin/bash
hadoop fs -rm -r /users/results
hadoop fs -rm hdfs:///users/mapper_get_users.py
hadoop fs -cp file:///home/hadoop/twitter/mapper_get_users.py hdfs:///users
