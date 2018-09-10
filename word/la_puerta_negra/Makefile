export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux


directories += la_puerta_negra/
directories += milonga/
directories += burundanga/
directories += tu_espalda_herida/

txtfiles = $(addsuffix contents.txt, $(directories))
texfiles = $(addsuffix contents.tex, $(directories))
aesfiles = $(addsuffix contents.aes, $(directories))

book.pdf: book.tex $(texfiles)
	# latexmk -pv -pdf book.tex
	#xelatex book.tex
	latexmk -xelatex book.tex

#la_puerta_negra/contents.tex: la_puerta_negra/contents.txt
#	python mtxt2tex.py -o $@ $<
#	../encrypt.sh $< la_puerta_negra/contents.aes

%.tex: %.txt
	python mtxt2tex.py -o $@ $<
	cd $(dir $<) && sh ../../encrypt.sh && cd ..

decrypt:
	sh ../decrypt_all.sh $(aesfiles)


c:	cleanup

cleanup:
	echo $(texfiles)
	python mtxt2tex.py -c -o la_puerta_negra/contents.out.txt la_puerta_negra/contents.in.txt
	python mtxt2tex.py -c -o milonga/contents.out.txt milonga/contents.in.txt
	python mtxt2tex.py -c -o burundanga/contents.out.txt burundanga/contents.in.txt
	python mtxt2tex.py -c -o tu_espalda_herida/contents.out.txt tu_espalda_herida/contents.in.txt

clean:
	latexmk -c

.PHONY: clean cleanup decrypt

t:
	echo $(texfiles)
