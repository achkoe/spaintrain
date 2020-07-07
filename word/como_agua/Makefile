export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

directories := ./

txtfiles = $(addsuffix contents.txt, $(directories))
texfiles = $(addsuffix contents.tex, $(directories))
aesfiles = $(addsuffix contents.aes, $(directories))


current := $(lastword $(texfiles))

current: book.tex $(current)
	$(file > chapters.tex,\input{$(current)})
	latexmk -xelatex -g book.tex


all := $(addsuffix }\clearpage,$(addprefix \input{,$(texfiles)))

all: book.tex $(texfiles)
	$(file > chapters.tex,$(all))
	latexmk -xelatex -quiet -g book.tex 1> xelatex.log 2>&1
	latexmk -xelatex -quiet -g dictionary.tex 1> xelatex.log 2>&1


%.tex: %.txt
	python mtxt2tex.py -o $@ $<
	python -c "import mtxt2tex as m; m.make_dictionary()"
	cd $(dir $<) && sh ../encrypt.sh && cd ..
	cd $(dir $<) && sh ../encrypt2.sh && cd ..


check:
	python mtxt2tex.py -o contents.tex contents.txt
	python -c "import mtxt2tex as m; m.make_dictionary()"

c: cleanup
cleanup:
	python mtxt2tex.py -c -o $(addsuffix .out.txt,$(basename $(current))) $(addsuffix .in.txt,$(basename $(current)))


decrypt:
	cd $(dir $(lastword $(aesfiles))) && sh ../../decrypt.sh && cd ..

decryptall:
	sh ../decryptall.sh $(directories)

view:
	xreader book.pdf &
