MAIN ?= tex/main.tex

.PHONY: pdf all clean cleanall

pdf:
	latexmk $(MAIN)

all: pdf

clean:
	latexmk -c $(MAIN)

cleanall:
	latexmk -C $(MAIN)
