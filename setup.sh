#!/bin/bash
git submodule update --init --recursive
sudo apt install python3-pip
sudo apt install ffmpeg
sudo cp nubiScan.service /etc/systemd/system
sudo pip3 install -r requirments.txt
sudo pip3 install -r kbdPicker/requirments.txt
sudo systemctl enable nubiScan
sudo systemctl start nubiScan
