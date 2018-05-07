book.pdf: book.tex el_paquete.tex
	latexmk -pv -pdf --silent $<

booklet.pdf: book.pdf
	./mkbooklet.py $< booklet.tex --simplex
	latexmk -pv -pdf booklet.tex


el_paquete.tex: el_paquete.txt
	python mtxt2tags.py -p -o $@ $<
	sh password.txt