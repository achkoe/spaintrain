export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

book.pdf: book.tex la_puerta_negra/contents.tex
	# latexmk -pv -pdf book.tex
	#xelatex book.tex
	latexmk -pv -xelatex book.tex

la_puerta_negra/contents.tex: la_puerta_negra/contents.txt
	python mtxt2tex.py -o $@ $<
	../encrypt.sh $< la_puerta_negra/contents.aes

c:	cleanup
	
cleanup: 
	python mtxt2tex.py -c -o la_puerta_negra/contents.out.txt la_puerta_negra/contents.in.txt 