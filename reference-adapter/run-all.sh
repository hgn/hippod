#!/bin/bash

#set -x

TEST=(0101-add-ten-entries.py 0101-add-ten-entries.py 0110-add-million-entries.py)
TEST2=(check-when-title-changed.sh check-when-categories-changed.sh \
       check-when-title-and-categories-changed.sh \
       check-when-one-char-changed.sh check-when-object-twice.sh)

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for i in "${TEST[@]}"; do
    echo -n "$i.. "
    rm -rf /tmp/hippod-db
    $DIR/../run.py -f $DIR/../assets/hippod-configuration.json 1>/dev/null 2>&1 &
    disown
    pid=$!
    sleep 2
    $DIR/$i --quite
    /bin/kill -9 $pid 1>/dev/null 2>&1
done

for j in "${TEST2[@]}"; do
    echo -n "$j.. "
    rm -rf /tmp/hippod-db
    $DIR/../run.py -f $DIR/../assets/hippod-configuration.json 1>/dev/null 2>&1 &
    disown
    pid=$!
    sleep 2
    /bin/bash $DIR/$j
    /bin/kill -9 $pid 1>/dev/null 2>&1
done