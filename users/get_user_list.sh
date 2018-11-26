#!/bin/bash

rm ./user_names_unique.txt

for file in ./data/*
do
  ./get_user_list.py < "$file" >> ./user_names.txt
done

chmod +777 ./user_names.txt
echo "total users:"
cat ./user_names.txt | wc -l
cat ./user_names.txt | uniq > ./user_names_unique.txt
echo "unique users:"
cat ./user_names_unique.txt | wc -l

rm ./user_names.txt
