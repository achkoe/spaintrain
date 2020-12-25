export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux
ifeq ($(MINGW_CHOST),x86_64-w64-mingw32)
	PYTHON = python
else
	PYTHON = python3
endif

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
	$(PYTHON) mtxt2output.py tex
	$(PYTHON) mtxt2output.py dictionary
	# cd $(dir $<) && sh ../encrypt.sh && cd ..
	cd $(dir $<) && sh ../encrypt2.sh && cd ..

ebook:
	$(PYTHON) mtxt2output.py ebook --configfile config.json

check:
	$(PYTHON) mtxt2output.py tex
	$(PYTHON) mtxt2output.py dictionary

c: cleanup
cleanup:
	$(PYTHON) mtxt2output.py cleanup


decrypt:
	cd $(dir $(lastword $(aesfiles))) && sh ../../decrypt.sh && cd ..

decryptall:
	sh ../decryptall.sh $(directories)

view:
	xreader book.pdf &
