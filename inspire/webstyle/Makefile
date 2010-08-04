# $Id$

include ../config.mk
-include ../config-local.mk

LIBFILES = webstyle_templates_inspire.py

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	@echo "Done."

install-ugly: uglify

uglify:
	@cat invenio_inspire_ugly.css >>$(WEBDIR)/img/invenio_inspire.css
	@mv $(WEBDIR)/img/inspire_logo_beta_ugly.png $(WEBDIR)/img/inspire_logo_beta.png

clean:
	@rm -f *.orig *~

# end of file
