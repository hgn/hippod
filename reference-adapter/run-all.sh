#!/bin/bash

#set -x

TEST=(0101-add-ten-entries.py 0101-add-ten-entries.py 0110-add-million-entries.py)

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for i in "${TEST[@]}"; do
    echo -n "$i.. "
    rm -rf $DIR/../instance
    $DIR/../run.py 1>/dev/null 2>&1 &
    disown
    pid=$!
    sleep 2
    $DIR/$i --quite
    /bin/kill -9 $pid 1>/dev/null 2>&1
done