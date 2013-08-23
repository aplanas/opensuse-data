#!/bin/bash

PREFIX=<LOCAL DIRECTORY>
URL=<LOCAL URL WHERE ARE THE LOGS>
NPROCS=4 # 6

function process_day {
    year=$1; month=$2; day=$3
    d=$year$month$day

    log=$URL/$year/$month/download.opensuse.org-$d-access_log.gz
    if curl -sIf -o /dev/null "$log"; then
	curl -s "$log" | gunzip | python log2db.py --dbenv $PREFIX/dbenv --db $d &> $PREFIX/logs/$d.txt
    fi
}


# If we don't say anything, we get since the beginning until today (excluded)
SINCE=${1:-"2010-01-01"}
LAST=${2:-`date -d "tomorrow" +%Y-%m-%d`}

echo "Converting from [$SINCE to $LAST)"


# Store the # on concurrent procs
count=0

current=$SINCE
while [ "$current" != "$LAST" ]; do
    # Extract date the components
    year=`echo $current | cut -d'-' -f1`
    month=`echo $current | cut -d'-' -f2`
    day=`echo $current | cut -d'-' -f3`

    echo "Converting $current ..."

    count=$((count + 1))
    ( process_day $year $month $day ) &

    if [ $((count % $NPROCS)) -eq 0 ]; then
	wait
    fi

    # Next day
    current=`date -d "$current +1 day " +%Y-%m-%d`
done

wait
