#!/usr/bin/env bash

PATH_DATA="~/tmp/allmail"
python main.py --perspective DOMAIN --transport FILE --file_store_path $PATH_DATA
