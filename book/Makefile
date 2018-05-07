
export PATH := /usr/local/texlive/2015/bin/x86_64-linux/:$(PATH)
SRC = aussprache.tex datumzeit.tex grammar.tex zahlen.tex cuerpo.tex deutsch.tex verwandschaft.tex verben.tex
SRC += zeiten_praesens.tex zeiten_estargerundio.tex zeiten_verbeninfinitiv.tex zeiten_imperativ.tex zeiten_preteritoperfecto.tex
SRC += zeiten_acabarde.tex zeiten_indefinido.tex zeiten_preteritoimperfecto.tex zeiten_irainfinitiv.tex zeiten_futurosimple.tex
SRC += zeiten_conditional.tex zeiten_subjuntivopresente.tex zeiten_plusquamperfecto.tex
SRC += pronomen_o1.tex
FLAGS = -CF -pdf 
X = --silent

all: book.pdf tbook.pdf pbook.pdf

view: book.pdf
	latexmk -pv -pdf --silent book.tex

book.pdf: book.tex $(SRC)
	latexmk $(FLAGS) $<

tbook.pdf: tbook.tex $(SRC)
	latexmk $(FLAGS) $<

pbook.pdf: pbook.tex 
	latexmk $(FLAGS)  $<

%.pdf: %.tex
	latexmk $(FLAGS)  $<	

pbook.tex: book.pdf
	python mkbooklet.py
	
%.tex: %.t2tin
	python mtxt2tags.py  -o $@ $<

.phony: clean veryclean

clean: 
	rm -f *.out  *.aux *.toc *.log $(SRC) *.fdb_latexmk *.fls $(SRC)

veryclean: clean
	rm -f *.pdf body.png *.epub book.html