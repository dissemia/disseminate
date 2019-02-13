.PHONY: build clean test
.DEFAULT_GOAL := build

TXT_DIR = txt
RST_DIR = rst

CLI_SRC := $(wildcard *.sh)
CLI_TXT := $(CLI_SRC:%.sh=$(TXT_DIR)/%.txt)
CLI_HTML := $(CLI_SRC:.sh=.html)
CLI_TEX := $(CLI_SRC:.sh=.tex)
CLI_RST := $(CLI_SRC:%.sh=$(RST_DIR)/%.rst)
CLI := $(CLI_SRC:.sh=)


errors = 0


$(TXT_DIR)/%.txt: %.sh ## Process the text output of commands
	@mkdir -p $(TXT_DIR)
	@chmod u+x ./$<
	@./$< > $@  # export the text file

	@rm -f *.pdb


%.html: %.sh
	@printf "$$" > tmp_$@
	@sed 's/^/ /g' $< >> tmp_$@
	@chmod u+x ./$<
	@FORCE_COLOR=TRUE ./$< >> tmp_$@
	@pygmentize -l shell-session -f html tmp_$@ | sed 's/^/    /g' >> tmp2_$@

	@echo ".. only:: html\n\n.. raw:: html\n" > $@
	@cat -e tmp2_$@ | sed 's/\$$$$//g' >> $@                            # Copy command output, strip non-print chars
	@echo '\n' >> $@

	@sed -i'.bak' 's/\"highlight\"/\"highlight console\"/g' $@  	    # Add 'console' class to html div
	@sed -i'.bak' 's/\^\[\[1m/<font style=\"font-weight:bold;\">/g' $@  # Replace bold codes
	@sed -i'.bak' 's/\^\[\[22m/<\/font>/g' $@                           # Replace closing codes for bold
	@sed -i'.bak' 's/\^\[\[36m/<font color=\"#008b8b\">/g' $@           # Replace cyan colors
	@sed -i'.bak' 's/\^\[\[91m/<font color=\"red\">/g' $@               # Replace red colors
	@sed -i'.bak' 's/\^\[\[92m/<font color=\"green\">/g' $@             # Replace green colors
	@sed -i'.bak' 's/\^\[\[33m/<font color=\"#abb51f\">/g' $@
	@sed -i'.bak' 's/\^\[\[94m/<font color=\"blue\">/g' $@              # Replace blue colors
	@sed -i'.bak' 's/\^\[\[95m/<font color=\"magenta\">/g' $@           # Replace magenta colors
	@sed -i'.bak' 's/\^\[\[96m/<font color=\"#008b8b\">/g' $@           # Replace cyan colors
	@sed -i'.bak' 's/\^\[\[0m/<\/font>/g' $@                            # Replace closing codes for colors

	@rm -f tmp_$@ tmp2_$@ *.bak *.pdb  # Remove temporary files


%.tex: %.sh
	@chmod u+x ./$<
	@FORCE_COLOR=TRUE ./$< >> tmp_$@
	@sed -i'.bak' 's/^/  /g' tmp_$@                           # Add a 2-spacetab at the start of every line

	@echo ".. only:: latex\n\n.. raw:: latex\n" > $@
	@echo "  \\\\begin{sphinxVerbatim}[commandchars=\\\\\\\\\\\\{\\\\},fontsize=\\\\small]" >> $@
	@printf "  \\\\textcolor{darkorange}{$$}" >> $@
	@sed 's/^/  /g' $< | sed 's/\\/\\textbackslash/g'>> $@
	@cat -e tmp_$@ | sed 's/\$$$$//g' >> $@                   # Copy command output, strip non-print chars
	@echo "  \\\\end{sphinxVerbatim}\n {} \n" >> $@

	@sed -i'.bak' 's/--/-{-}/g' $@                            # Preserve --
	@sed -i'.bak' 's/\^\[\[1m/\\textbf{/g' $@                 # Replace bold codes
	@sed -i'.bak' 's/\^\[\[22m/}/g' $@                        # Replace closing bold codes
	@sed -i'.bak' 's/\^\[\[36m/\\textcolor{cyan}{/g' $@       # Replace cyan colors
	@sed -i'.bak' 's/\^\[\[91m/\\textcolor{red}{/g' $@        # Replace red colors
	@sed -i'.bak' 's/\^\[\[92m/\\textcolor{olivegreen}{/g' $@ # Replace green colors
	@sed -i'.bak' 's/\^\[\[33m/\\textcolor{darkyellow}{/g' $@ # Replace dark yelow colors
	@sed -i'.bak' 's/\^\[\[94m/\\textcolor{blue}{/g' $@       # Replace blue colors
	@sed -i'.bak' 's/\^\[\[95m/\\textcolor{magenta}{/g' $@    # Replace magenta colors
	@sed -i'.bak' 's/\^\[\[96m/\\textcolor{cyan}{/g' $@       # Replace cyan colors
	@sed -i'.bak' 's/\^\[\[0m/}/g' $@                         # Replace closing codes for colors

	@rm -f tmp_$@ *.bak *.pdb # Remove temporary files


$(RST_DIR)/%.rst: %.html %.tex
	@mkdir -p $(RST_DIR)
	@cat $? > $@
	@rm $?


test: build ## Test the CLI output against the reference .txt files
	@for i in $(CLI); do \
		printf "Testing \033[1m$$i.sh\033[22m\n" ; \
		chmod u+x ./$$i.sh ; \
		./$$i.sh | diff txt/$$i.txt - || exit 1 ; \
		return_value=$$? ; \
	done
	@rm -f tmp.out *.pdb


clean:  ## Clean the output files
	@find . -name '*.txt' -exec rm -f {} +
	@find . -name '*.tex' -exec rm -f {} +
	@find . -name '*.html' -exec rm -f {} +
	@find . -name '*.rst' -exec rm -f {} +
	@find . -name '*.pdb' -exec rm -f {} +


build: $(CLI_TXT) $(CLI_RST)  ## Build the CLI .txt outputs and documentation .rst
	@printf '\033[92mCLI files built\033[0m\n'


help:  ## Print this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
