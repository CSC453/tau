MILESTONEDIR=tau/milestones
INFODIR=tau/milestones/info

for test in $MILESTONEDIR/*.toml; do
    fname="${test%.toml}"
    basename="${fname##*/}"
    listname="$MILESTONEDIR/$basename.list"
    echo Processing $test $listname
    python3 -m tau.utilities.mkcharacter match --pattern $test "$INFODIR"/*.toml > "$listname"
done