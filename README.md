
# Hardware setup

## Linux
This software should run on any Linux box. It assumes these things:
1. Input devices are mounted in /dev/input
2. Systemd is manageing the deamons
3. Network connectivity
4. Audio out device

So long as these requirements are met you should not have a problem running nubiScan. Though it is assumed you will want to run this on a Raspberry Pi.

## The bar-code Scanner
Any bar-code scanner that enumerates as a keyboard will work so long as it can read both 1d and 2d bar-codes. There are many to choose from. Both wired and wireless scanners are available. Here is a link to the first bar-code scanner we've used: [Eyoyo Handheld USB 2D Barcode Scanner](https://www.amazon.com/gp/product/B088QV215Y/ref=ox_sc_act_title_2?smid=A1UYJA9LD7FIS5&psc=1)


# Software setup

## Raspberry Pi
Skip this section if you already have a system set up.

The steps to setup a new Raspberry Pi system are:
1. Install a Linux image onto an sd card
2. Configure it for network access
3. Set the default audio out device

### Picking and installing a Linux image
Do these steps from your Windows or Mac.
1. Pick and download an OS: The official Raspberry Pi OS Linux images can be found here: [Raspberry Pi operating systems](https://www.raspberrypi.org/software/operating-systems/)
Pick whichever one you like. I prefer the 'Raspberry Pi OS Lite' image because it is smaller. But you might prefer one that has desktop support, with a more traditional GUI.

2. Next you need to download an installer from here: [Raspberry Pi Imager](https://www.raspberrypi.org/software/)

3. Install the imager and follow it's instructions for installing the OS you downloaded in step one.

### Pre-configure your new Raspberry Pi image
Also do these steps from your Windows or Mac. 
1. The network:
   * Setup wifi for nubiNet: [Setting up a Raspberry Pi headless](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)
   * Enable ssh: Follow instructions in section three 'Enable SSH on a headless Raspberry Pi' [SSH (Secure Shell)](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md)
   * Change its hostname:

### First time boot
1. Remove the SD card from your computer and put in into the Raspberry Pi.
2. Plug the Pi into the USB-C power supply.
3. Wait a minute or so for the system to boot and configure itself.
4. ssh into the system (see section 'ssh')
5. Change the default password: ```passwd <new password>```
6. Change the hostname to nubiscanX where X is the count of installed scanners. ```sudo hostnamectl set-hostname nubiscanX```
7. Update the system: ```sudo apt update && sudo apt full-upgrade```
8. Install git: ```sudo apt install git```
9. Install the nubiScan software: ```git clone ?????```
10. Copy the service account credentials to the ~/nubiScan directory. (also see the Service Account section)
11. Setup the nubiScan software: ```~/nubiScan/setup.sh```
12. Reboot: ```sudo reboot``` 
13. Plug in the bar-code scanner and you are ready to go.

## ssh

## What is a service account
A service account is a special type of Google account that isn't for people, its for robots. Once you have a service account setup, you will be issues a Google identity (an email address). You can then share any Google doc with this new identity. To do that you would do it the same way you would share a document with a person. Find the 'share' settings and add the service accounts email address. 

[More than you will ever need to know about Google service accounts](https://cloud.google.com/docs/authentication/production)

## Adding an existing service account
I've already created a service account for this purpose, nubiBot2000. But there is nothing special about it. You can also create a new one. It's safe to use several accounts so long as you are also sharing the appropriate Google docs with it. But because its quite tedious to create one and because there is no advantage of using several accounts I can give you a copy of nubiBot2000's credentials file. The credentials work as the password to the service account it should be protected and handled with care. This is why it's not checked in to this repo. This is also why its important to change the default password. 

## Setting up a new service account
See [More than you will ever need to know about Google service accounts](https://cloud.google.com/docs/authentication/production)


# Systemd and starting nubiScan.py on boot
The setup.sh script sets this up for you with these two commands:
```
sudo systemctl enable nubiScan
sudo systemctl start nubiScan
```
The first command tells it to automaticaly start on boot. The second one starts it right now.
You can check the status of a running process with this command:
```
sudo systemctl status nubiScan
```
You can stop it like this:
```
sudo systemctl stop nubiScan
```

# Diagrams
![Block diagram](nubiScan.svg)

# Techncal references
* [More than you will ever need to know about Google service accounts](https://cloud.google.com/docs/authentication/production)
* [Google Sheets API](https://developers.google.com/sheets/api/reference/rest)
* [Python wrapper for Google's TTS service](https://gtts.readthedocs.io/en/latest/module.html#module-gtts.tts)

