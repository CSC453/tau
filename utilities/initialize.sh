# This bash script initializes a student's new repository with stub versions of the files they
# will need to complete the project.
#
# Any file of the form 'foo.template' will be copied to 'foo' if 'foo' does not.
#
# Any file of the form 'foo.toml' will be used to generate 'foo.py' if 'foo.py' does not.
# The command used to generate 'foo.py' is:
#   python3 -m tau.utilities.mktemplate --spec foo.toml --output foo.py

for file in tau/stubs/*.template; do
    fname="${file%.template}"
    basename="${fname##*/}"
    if [ ! -f "$basename" ]; then
        cp "$file" "$basename"
    else
        echo "$basename already exists"
    fi
done

for spec in tau/stubs/*.toml; do
    fname="${spec%.toml}"
    basename="${fname##*/}"
    pyname="$basename.py"
    if [ ! -f "$pyname" ]; then
        python3 -m tau.utilities.mktemplate --spec "$spec" --output "$pyname"
        # black --quiet "$pyname"
    else
        echo "$pyname already exists"
    fi
done
