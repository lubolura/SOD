#!/bin/bash

# Install Python modules
python3 setup.py install

# Install executables
install -m 755 sod /usr/bin

# Install config file read-only root permissions

if [ -r /etc/sod.cfg ]
then
  echo "Skipping install for sod.cfg file - file already exists!"
else
  install -m 600 sod.cfg /etc
fi

# Install detection model data
DATADIR=/usr/share/sod
#rm -rf $DATADIR
mkdir $DATADIR
cp -r model_data/* $DATADIR
chmod +rx $DATADIR
find $DATADIR -type d -exec chmod +rx {} \;
find $DATADIR -type f -exec chmod +r {} \;

# Install systemd service
cp sod.service /etc/systemd/system
systemctl daemon-reload
systemctl enable sod.service
systemctl start sod.service
