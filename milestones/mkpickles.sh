MILESTONEDIR=tau/milestones
LISTDIR=$MILESTONEDIR/lists
SPECSDIR=$MILESTONEDIR/specs

for test in $SPECSDIR/*.toml; do
    fname="${test%.toml}"
    basename="${fname##*/}"
    listname="$LISTDIR/$basename.list"
    picklefile="$MILESTONEDIR/$basename.pickle"
    if [ ! -f "$listname" ]; then
        echo "ERROR: $listname missing"
        continue
    fi
    echo Processing $test $listname
    func=$(yq .function $test)
    if [ "$func" == "null" ]; then
        echo "ERROR: $test missing function"
        continue
    fi
    compare=$(yq .compare $test)
    if [ "$compare" == "null" ]; then
        echo "ERROR: $test missing compare"
        continue
    fi
    python3 -m testerator.main create --text \
        --function $func \
        --compare $compare \
        --output "$picklefile" \
        $(cat "$listname")

    python3 -m testerator.main run "$picklefile" > /tmp/"$basename.verify"
done
