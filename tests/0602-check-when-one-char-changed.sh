#!/bin/bash

#set -x

TEST=(0303-same-object-default.py 0303-same-object-one-char-changed-in-data.py)

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# hardcoded path to hippod-db
rm -rf /tmp/hippod-db
$DIR/../run.py -f $DIR/../assets/hippod-configuration.json 1>/dev/null 2>&1 &
disown
pid=$!

for i in "${TEST[@]}"; do
    echo -n "$i.. "
    sleep 2
    $DIR/$i --quite
done
/bin/kill -9 $pid 1>/dev/null 2>&1