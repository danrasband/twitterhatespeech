#!/bin/bash

for file in ./data/*
do
  ./get_user_names.py < "$file" >> ./user_names.txt
done

chmod +777 ./user_names.txt
echo "total users:"
cat ./user_names.txt | wc -l
echo "unique users:"
cat ./user_names.txt | uniq | wc -l
