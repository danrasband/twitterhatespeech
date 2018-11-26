# Pulling user information:

All of the below assumes that `Python3.6` and `pip3.6` have been installed and can be called with `python3.6` and `pip3.6`. 

#### 1. create config.py file with the following contents:

```
consumer_key = "xxx"
consumer_secret = "xxx"
access_key = "xxx"
access_secret = "xxx"
```

#### 2. create folder `data`

#### 3. install `twitter` package:

```
pip3.6 install twitter
```

#### 4. copy the following files to your current directory and make them executable with `chmod +777 filename`:
 
 - `users/get_users.py`
 - `users/key_words.txt`
 - `users/get_counts.sh`
 - `users/get_user_names.py`
 - `users/get_user_names.sh`

#### 5. run the following command to generate complete user info files based on selected key words:

```
./get_users.py < key_words.txt
```

#### 6. check how many uses in each file:

```
./get_counts.sh
```

My output:
```
./data/user_list_1488.txt
58
./data/user_list_altright.txt
83
./data/user_list_fashy.txt
44
./data/user_list_identitarian.txt
122
./data/user_list_nationalist.txt
796
./data/user_list_nationalsocialism.txt
14
./data/user_list_nazi.txt
566
./data/user_list_redpill.txt
262
```

#### 7. extract screen names only for further analysis:

```
./get_user_names.sh
```

My output:
```
total users:
1945
unique users:
1906
```

#### 8. full list of screen names will be stored in `user_names.txt`
