all: book.pdf

booklet.pdf: book.pdf
	./mkbooklet.py $< booklet.tex --simplex
	latexmk -pv -pdf booklet.tex

view: book.pdf
	latexmk -pv -pdf book.tex

book.pdf: main.tex
	latexmk -CF -pdf book.tex

main.tex: main.t2t contents.t2tout 
	txt2tags -H -o $@ $<

contents.t2tout: contents.t2tin
	python ../../book/processtable.py $<

.phony: clean veryclean

clean: 
	rm -f table???.tex book.aux book.toc book.log contents.t2tout contents.tex main.tex

veryclean: clean
	rm -f book.pdf