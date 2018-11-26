#!/bin/bash

for file in ./data/*
do
  echo "$file"
  cat "$file" | wc -l
done
