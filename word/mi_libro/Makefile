export PATH := $(PATH):/usr/local/texlive/2015/bin/x86_64-linux

SOURCE = $(wildcard *.tex)
TEMP = $(addsuffix .ptex, $(basename $(SOURCE)))


book.pdf: $(TEMP)
	latexmk -xelatex book.ptex

%.ptex: %.tex
	python3 preprocess.py -r $< $@

.PHONY: t view clean, pure

view:
	start '/c/program\ files\ \(x86\)/Ghostgum/gsview/gsview64' book.pdf

t:
	echo $(SOURCE)
	echo $(TEMP)

clean:
	latexmk -c
	$(RM) $(TEMP)