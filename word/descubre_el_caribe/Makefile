export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

book.pdf: book.tex contents.tex
	# latexmk -pv -pdf book.tex
	#xelatex book.tex
	latexmk -pv -xelatex book.tex

contents.tex: contents.txt
	python mtxt2tex.py -o $@ $<
	../encrypt.sh

c:	cleanup
	
cleanup: 
	python mtxt2tex.py -c -o contents.out.txt contents.in.txt 