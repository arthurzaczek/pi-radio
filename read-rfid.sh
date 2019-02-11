#!/bin/bash

pipe=/tmp/rfidpipe

trap "rm -f $pipe" EXIT

if [[ ! -p $pipe ]]; then
	mkfifo $pipe
fi

while :
do
        read tag
        echo $tag > $pipe
done

