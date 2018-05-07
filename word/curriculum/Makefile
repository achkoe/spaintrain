export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

curriculum.pdf: curriculum.tex contents.tex
	latexmk -pv -pdf curriculum.tex

contents.tex: contents.txt
	python mtxt2tex.py -o $@ $<