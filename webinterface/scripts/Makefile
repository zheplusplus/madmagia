STEKIN=stekin -i window -i document -i jQuery -i mad
OUTPUT_DIR=../static/output/js

all:output_dir $(OUTPUT_DIR)/madmagia.js
	@echo "Done"

output_dir:
	@mkdir -p $(OUTPUT_DIR)

$(OUTPUT_DIR)/madmagia.js:gettext.js common.stkn projects.stkn workspace.stkn \
                          prepare.stkn edit.stkn player.stkn
	cat gettext.js > $@
	$(STEKIN) < common.stkn >> $@
	$(STEKIN) < prepare.stkn >> $@
	$(STEKIN) < projects.stkn >> $@
	$(STEKIN) < workspace.stkn >> $@
	$(STEKIN) < edit.stkn >> $@
	$(STEKIN) < player.stkn >> $@

clean:
	rm -f $(OUTPUT_DIR)/*
