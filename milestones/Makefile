all: info lists pickles

info:
	(cd ../..; ./tau/milestones/mkinfo.sh)

lists:
	(cd ../..; ./tau/milestones/mklists.sh)

pickles:
	rm -fr /tmp/*.verify
	(cd ../..; ./tau/milestones/mkpickles.sh)
	grep -v passed /tmp/*.verify || true

%.json: %.toml
	yq -p toml $< -oj > $@

clean:
	rm -f *.pickle ./lists/*.list ./info/*.toml
