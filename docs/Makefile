MILESTONES = \
	milestone02-3.pdf \
	milestone04-5.pdf \
	milestone06.pdf \
	milestone07.pdf \
	milestone08.pdf \
	milestone09.pdf \
	milestone10.pdf \
	milestone11-14-Final.pdf \
	milestoneVM.pdf \
	all.pdf

all: language.pdf $(MILESTONES)

%.pdf : %.typ
	typst compile $<

clean:
	rm -f $(MILESTONES) language.pdf