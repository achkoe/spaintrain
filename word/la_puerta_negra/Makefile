export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

directories := la_puerta_negra/ milonga/ burundanga/ tu_espalda_herida/ bano_de_sangre/ sin_cobertura/ la_didactica_del_miedo/
directories += esa_nave_me_llevara_para_siempre/
directories += el_precio_del_alabastro/
directories += los_ninos_del_cuenta/
directories += t/

txtfiles = $(addsuffix contents.txt, $(directories))
texfiles = $(addsuffix contents.tex, $(directories))
aesfiles = $(addsuffix contents.aes, $(directories))


current := $(lastword $(texfiles))

ankifile = anki.txt

current: book.tex $(current)
	$(file > chapters.tex,\input{$(current)})
	latexmk -xelatex -g book.tex


all := $(addsuffix }\clearpage,$(addprefix \input{,$(texfiles)))

all: book.tex $(texfiles)
	$(file > chapters.tex,$(all))
	latexmk -xelatex -g book.tex


%.tex: %.txt
	python mtxt2tex.py -o $@ $< >> anki.txt
	cd $(dir $<) && sh ../../encrypt.sh && cd ..

_anki:
	rm -f $(ankifile)
	touch $(ankifile)

anki: _anki $(texfiles)

c: cleanup
cleanup:
	python mtxt2tex.py -c -o $(addsuffix .out.txt,$(basename $(current))) $(addsuffix .in.txt,$(basename $(current)))


decrypt:
	cd $(dir $(lastword $(aesfiles))) && sh ../../decrypt.sh && cd ..

decryptall:
	sh ../decryptall.sh $(directories)

view:
	xreader book.pdf &
