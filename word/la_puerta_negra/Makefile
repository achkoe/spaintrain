export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

directories = la_puerta_negra/ test/

txtfiles = $(addsuffix contents.txt, $(directories))
texfiles = $(addsuffix contents.tex, $(directories))

book.pdf: book.tex $(texfiles)
	# latexmk -pv -pdf book.tex
	#xelatex book.tex
	latexmk -pv -xelatex book.tex

#la_puerta_negra/contents.tex: la_puerta_negra/contents.txt
#	python mtxt2tex.py -o $@ $<
#	../encrypt.sh $< la_puerta_negra/contents.aes

%.tex: %.txt
	python mtxt2tex.py -o $@ $<
	../encrypt.sh $< $(addsuffix .aes, $(basename $<))


c:	cleanup
	
cleanup: 
	python mtxt2tex.py -c -o la_puerta_negra/contents.out.txt la_puerta_negra/contents.in.txt 

clean:
	latexmk -c
	
t:
	echo $(texfiles)