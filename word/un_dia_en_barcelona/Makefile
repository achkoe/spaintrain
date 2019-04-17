export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

book.pdf: book.tex contents.tex
	# latexmk -pv -pdf book.tex
	latexmk -pv -xelatex book.tex

contents.tex: contents.txt
	python mtxt2tex.py -o $@ $<
	cd $(dir $<) && sh ../encrypt.sh && cd ..
	#sh password.txt
