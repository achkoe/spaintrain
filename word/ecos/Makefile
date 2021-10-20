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

txtfiles = $(addsuffix .txt, $(srcfiles))
texfiles = $(addsuffix .tex, $(srcfiles))
aesfiles = $(addsuffix .aes, $(srcfiles))
dicfiles = $(addprefix d_, $(texfiles))


current := $(lastword $(texfiles))
dcurrent := $(lastword $(dicfiles))

test: encrypt
	echo $(dicfiles)

encrypt:
	@echo "ENCRYPT"
	tar -cf contents.tar $(txtfiles)
	sh ../encryptfile.sh contents.tar contents.aes2

decrypt:
	sh ../decryptfile.sh contents.aes2 contents.tar
	tar -xvf contents.tar

current: book.tex $(current) encrypt
	$(file > chapters.tex,\input{$(current)}) $(file >> chapters.tex,\input{$(dcurrent)})
	latexmk -xelatex -g book.tex

all := $(addsuffix }\clearpage,$(addprefix \input{,$(texfiles)))

all: book.tex $(texfiles) encrypt
	cat $(texfiles) > contents.tex
	$(PYTHON) mtxt2output.py dictionary
	$(file > chapters.tex,$(all))
	latexmk -xelatex -quiet -g book.tex # 1> xelatex.log 2>&1
	#latexmk -xelatex -quiet -g dictionary.tex 1> xelatex.log 2>&1


%.tex: %.txt
	cp $< contents.txt
	$(PYTHON) mtxt2output.py tex
	cp contents.tex $@
	$(PYTHON) mtxt2output.py dictionary
	cp ddictionary.tex d_$@

ebook:
	$(PYTHON) mtxt2output.py ebook --configfile config.json

check:
	$(PYTHON) mtxt2output.py tex
	$(PYTHON) mtxt2output.py dictionary

c: cleanup
cleanup:
	$(PYTHON) mtxt2output.py cleanup

view:
	$(VIEW) book.pdf &
