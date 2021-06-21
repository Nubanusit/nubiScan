#!/bin/bash
git submodule update --init --recursive
sudo pip3 install -r requirments.txt
sudo pip3 install -r kbdPicker/requirments.txt
sudo apt install ffmpeg
sudo cp nubiScan.service /etc/systemd/system
sudo systemctl enable nubiScan
sudo systemctl start nubiScan
