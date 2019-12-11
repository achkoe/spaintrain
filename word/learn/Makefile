export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

files := deberes_2019_11_28 dia_de_muertos texto_2019_12_05

txtfiles = $(addsuffix .txt, $(files))
texfiles = $(addsuffix .tex, $(files))
aesfiles = $(addsuffix .aes, $(files))


current := $(lastword $(texfiles))

current: book.tex $(current)
	@echo $(txtfiles)
	$(file > contents.tex,\input{$(current)})
	latexmk -xelatex -g book.tex


all := $(addsuffix }\clearpage,$(addprefix \input{,$(texfiles)))

all: book.tex $(texfiles)
	$(file > chapters.tex,$(all))
	#latexmk -xelatex -g book.tex


%.tex: %.txt
	python mtxt2tex.py -o $@ $<
	echo $(basename $<)
	cd $(dir $<) && sh ../encrypt_file.sh $< $(addsuffix .aes, $(basename $<)) && cd ..


c: cleanup
cleanup:
	python mtxt2tex.py -c -o $(addsuffix .out.txt,$(basename $(current))) $(addsuffix .in.txt,$(basename $(current)))


decrypt:
	cd $(dir $(lastword $(aesfiles))) && sh ../../decrypt.sh && cd ..

decryptall:
	sh ../decryptall.sh $(directories)

view:
	xreader book.pdf &
