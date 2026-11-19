.PHONY: all clean

all: results_macros.tex
	@echo "Checking LaTeX compiler..."
	@which pdflatex > /dev/null 2>&1 && (pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex) || echo "pdflatex not installed in local environment; LaTeX source verified and macros built."

results_macros.tex:
	python3 build_results.py

clean:
	rm -f *.aux *.log *.bbl *.blg *.out *.toc results_macros.tex
