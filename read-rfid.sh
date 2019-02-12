#!/bin/bash

pipe=/tmp/rfidpipe

echo "Starting RFID Pipe Service"

trap "rm -f $pipe" EXIT

if [[ ! -p $pipe ]]; then
	mkfifo $pipe
	echo "Pipe created"
fi

echo "listening to tty"

while :
do
        read tag
        echo $tag > $pipe
	echo $tag
done

