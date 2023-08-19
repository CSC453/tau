MILESTONEDIR=tau/milestones
MILESTONESPECDIR=$MILESTONEDIR/specs
INFODIR=$MILESTONEDIR/info
LISTSDIR=$MILESTONEDIR/lists

for test in $MILESTONESPECDIR/*.toml; do
    fname="${test%.toml}"
    basename="${fname##*/}"
    listname="$LISTSDIR/$basename.list"
    echo Processing $test $listname
    echo python3 -m tau.utilities.mkcharacter match --pattern $test "$INFODIR"/*.toml > "$listname"

    python3 -m tau.utilities.mkcharacter match --pattern $test "$INFODIR"/*.toml > "$listname"
done
