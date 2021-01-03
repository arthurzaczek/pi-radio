# pi radio

A raspberry pi radio device

## Softwaresetup

1) Install software (see below)

2) Clone this repository to your PI

3) Mount a share (samba) to `/mnt/music`

   e.g. samba (/etc/fstab)

       //my-nas/Multimedia/MP3/Kinder /mnt/music cifs  username=myuser,password=mypassword  0  0

4) Then create 2 systemd units (see Systemd)

5) Todo: The wirering is hardcoded yet.

## Install software

    apt install sox mpd mpc screen git python3 python3-pip
	pip3 install RPi.GPIO
	
upnp is provided by: https://www.lesbonscomptes.com/upmpdcli/index.html	
	
## Systemd

**/etc/systemd/system/radio.service**
	
	[Unit]
	Description=Radio Service
	After=multi-user.target

	[Service]
	User=pi
	Type=idle
	ExecStart=/usr/bin/python3 /home/pi/pi-radio/radio.py
	WorkingDirectory=/home/pi/pi-radio
	Restart=on-failure
	StandardInput=tty
	StandardOutput=tty
	TTYPath=/dev/tty2

	[Install]
	WantedBy=multi-user.target
	
**/etc/systemd/system/my-tty1.service**

This will redirect keyboard input (from the rfid reader) to a named pipe

See: [https://superuser.com/questions/473411/redirect-physical-keyboard-input-to-ssh/1299783#1299783](https://superuser.com/questions/473411/redirect-physical-keyboard-input-to-ssh/1299783#1299783)

    [Unit]
	Description=my tty1-service
	After=getty.target
	Conflicts=getty@tty1.service

	[Service]
	Type=simple
	ExecStart=/usr/bin/screen -S myTTY1 /home/pi/pi-radio/read-rfid.sh
	StandardInput=tty-force
	StandardOutput=inherit
	StandardError=inherit

	[Install]
	WantedBy=multi-user.target


Call this to enable services

    systemctl daemon-reload
	systemctl enable radio
	systemctl enable my-tty1

## cards.json

    {
            "0003599777": {
                    "folder": "Bob der Baumeister"
            },
            "0014038694": {
                    "folder": "Paw Patrol - 1"
            }
    }
    
---------	--------------------------------------
Property	Description
---------	--------------------------------------
0003599777	This is the number of the RFID Card

folder		The relative path to the folder to play
---------	--------------------------------------
