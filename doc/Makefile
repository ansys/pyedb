# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -j auto --color
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

.install-deps:
	@pip freeze | grep -q "pypandoc_binary" && is_pypandoc_binary_installed="yes" || is_pypandoc_binary_installed="no"
	@if [ "${ON_CI}" = "True" ] && [ "$$is_pypandoc_binary_installed" != "yes" ]; then \
		@echo "Removing pypandoc to avoid conflicts with pypandoc-binary needed for CI/CD"; \
		pip uninstall --yes pypandoc; \
		@echo "Installing pypandoc-binary"; \
		pip install pypandoc-binary==1.13; \
	fi

clean:
	rm -rf $(BUILDDIR)/*
	rm -rf examples/
	find . -type d -name "_autosummary" -exec rm -rf {} +

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: .install-deps Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# build html docs in parallel using all available CPUs
# WARNING: this is a resource hog
html: .install-deps
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -j auto

# Build pdf docs.
pdf: .install-deps
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/pyedb.pdf && echo pdf exists) || exit 1
