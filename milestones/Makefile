all:
	rm -fr /tmp/*.verify
	(cd ../..; ./tau/milestones/mkinfo.sh)
	(cd ../..; ./tau/milestones/mklists.sh)
	(cd ../..; ./tau/milestones/mkpickles.sh)
	grep -v passed /tmp/*.verify || true

%.json: %.toml
	yq -p toml $< -oj > $@

clean:
	rm -f *.pickle ./lists/*.list ./info/*.toml
