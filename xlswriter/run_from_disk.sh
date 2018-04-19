#!/usr/bin/env bash

source ~/builds/venv_containers/bin/activate
DATA="/Users/polfilm/tmp/offlineimap"

#python main.py --perspective DOMAIN --sections 'EmailAddress,Urls,Schemes,SubDomains' --transport FILE --file_store_path $DATA --verbose

#python main.py --perspective DOMAIN --transport FILE --file_store_path $DATA --verbose
#python main.py --perspective DOMAIN --sections 'EmailAddress,Urls,Schemes,SubDomains' --transport FILE --file_store_path $DATA --verbose
python main.py --perspective EMAILADDRESS --transport FILE --file_store_path $DATA --verbose
