#!/usr/bin/env bash

PATH_DATA="~/tmp/allmail"
python main.py --perspective DOMAIN --sections 'Email Address,Urls' --transport FILE --file_store_path $PATH_DATA
