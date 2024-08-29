TESTDIR=tau/tests
OUTDIR=tau/milestones/info

for test in $TESTDIR/*.tau; do
    fname="${test%.tau}"
    basename="${fname##*/}"
    infoname="$OUTDIR/$basename.toml"
    echo Processing $test $infoname
    python3 -m tau.utilities.mkcharacter characterize --output "$infoname" "$test"
done
