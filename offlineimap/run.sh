#!/bin/bash -exak

echo "
[general]
dry-run = False
ui = ttyui
accounts = gmail
fsync = False
pythonfile = $PATH_DATA/.utf7.py

[Account gmail]
localrepository = gmail-local
remoterepository = gmail-remote
status_backend = sqlite

[Repository gmail-local]
sep = .
type = Maildir
remoteuser = $REMOTE_USER
localfolders = $PATH_DATA/$REMOTE_USER


[Repository gmail-remote]
readonly = True
maxconnections = 1
type = Gmail
remoteuser = $REMOTE_USER
oauth2_client_id = $CLIENT_ID
oauth2_client_secret = $CLIENT_SECRET
oauth2_refresh_token = $OAUTH_REFRESH_TOKEN
sslcacertfile = /etc/ssl/certs/ca-certificates.crt
realdelete = no


nametrans: lambda s: {'[Gmail]/All Mail':'allmail'}.get(s, s).decode('imap4-utf-7').encode ('utf8')
folderfilter = lambda foldername: foldername in ['[Gmail]/All Mail', '[Google Mail]/All Mail']



" > $PATH_DATA/.offlineimaprc.$REMOTE_USER

/usr/bin/python2.7 $PATH_APP/offlineimap -c $PATH_DATA/.offlineimaprc.$REMOTE_USER
rm $PATH_DATA/.offlineimaprc.$REMOTE_USER
