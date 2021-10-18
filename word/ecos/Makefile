export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux
ifeq ($(MINGW_CHOST),x86_64-w64-mingw32)
	PYTHON = python
	VIEW = "C:\Program Files (x86)\Ghostgum\gsview\gsview64.exe"
else
	PYTHON = python3
	VIEW = xreader
endif

directories := ./
srcfiles = ecos_20_13_p11
srcfiles += ecos_test

txtfiles = $(addsuffix .txt, $(srcfiles))
texfiles = $(addsuffix .tex, $(srcfiles))
aesfiles = $(addsuffix .aes, $(srcfiles))
dicfiles = $(addprefix d_, $(texfiles))


current := $(lastword $(texfiles))

test:
	echo $(dicfiles)

current: book.tex $(current)
	$(file > chapters.tex,\input{$(current)})
	latexmk -xelatex -g book.tex

# TODO: dictionary handling
all := $(addsuffix }\clearpage,$(addprefix \input{,$(texfiles)))

all: book.tex $(texfiles)
	$(file > chapters.tex,$(all))
	#latexmk -xelatex -quiet -g book.tex 1> xelatex.log 2>&1
	#latexmk -xelatex -quiet -g dictionary.tex 1> xelatex.log 2>&1


%.tex: %.txt
	cp $< contents.txt
	$(PYTHON) mtxt2output.py tex
	cp contents.tex $@
	$(PYTHON) mtxt2output.py dictionary
	cp ddictionary.tex d_$@
	# cd $(dir $<) && sh ../encrypt.sh && cd ..
	#cd $(dir $<) && sh ../encrypt2.sh && cd ..

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
	$(VIEW) book.pdf &
