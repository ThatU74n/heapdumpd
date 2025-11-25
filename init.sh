#!/bin/bash 

mkdir -p ~/heapdump/dump

cp ./heapdump-server.service /etc/systemd/system/heapdump-server.service

sudo systemctl daemon-reload
sudo systemctl enable heapdump-server.service
