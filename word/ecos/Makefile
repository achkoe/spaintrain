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


all := $(addsuffix }\clearpage,$(addprefix \input{,$(texfiles)))

all: book.tex $(texfiles) encrypt
	$(file > chapters.tex,$(all))
	$(PYTHON) mtxt2output.py dictionary
	latexmk -xelatex -quiet -g book.tex ##1> xelatex.log 2>&1

%.tex: %.txt
	$(PYTHON) mtxt2output.py tex

check:
	$(PYTHON) mtxt2output.py tex
	$(PYTHON) mtxt2output.py dictionary

c: cleanup
cleanup:
	$(PYTHON) mtxt2output.py cleanup

encrypt:
	@echo "ENCRYPT"
	sh ../encryptfile.sh contents.txt contents.aes2

decrypt:
	cd $(dir $(lastword $(aesfiles))) && sh ../../decrypt.sh && cd ..

decryptall:
	sh ../decryptall.sh $(directories)

view:
	xreader book.pdf &
