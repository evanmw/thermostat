#!/usr/bin/env bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo apt update
sudo apt upgrade
sudo apt install -y build-essential python-dev python-pip
sudo pip install -y RPi.GPIO

# Bluetooth things
sudo apt install -y bluetooth
sudo pip install -y pybluez

# Dependencies for the screen
sudo apt install -y python-imaging python-smbus

# i2c setup
sudo apt install -y python-smbus i2c-tools
sudo i2c-dev >> /etc/modules
if [ -f /boot/config.txt ]; then
    sed -i '/i2c_arm/s/^#//g' /boot/config.txt # uncomment ine with "i2c_arm" in config file
    sed -i '/i2c1/s/^#//g' /boot/config.txt
fi
if [ -f /etc/modprobe.d/raspi-blacklist.conf ]; then
    sed -i '/i2c-bcm2708/s/^/#/g' /etc/modprobe.d/raspi-blacklist.conf
    sed -i '/spi-bcm2708/s/^/#/g' /etc/modprobe.d/raspi-blacklist.conf
fi
sudo adduser pi i2c

# add onewire support for the DS18B20 temperature sensor
sudo echo "#Enable 1-wire support" >> /boot/config.txt
sudo echo "dtoverlay=w1-gpio" >> /boot/config.txt

# PWM
sudo pip install -y wiringpi


pushd $ROOT
git submodule update --init --recursive
pushd Adafruit_Python_SSD1306
sudo python setup.py install
popd
popd

echo "Enabling I2C and 1-wire requires a resboot."
echo "Type 'y [enter]' to reboot now."
read INPUT

if [ $INPUT == 'y' ]; then
    sudo reboot
fi