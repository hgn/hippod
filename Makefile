EXEC_DIR = /var/www/hippod


help:
	@echo "install - install distribution to /var/www/hippod and systemd unit file"

all:
	help

install:
	@if [ -d "$(EXEC_DIR)" ] ; \
	then \
		echo "$(EXEC_DIR) present, remove first" ; \
		exit 1 ; \
	fi 
	mkdir -p $(EXEC_DIR)
	cp -r . $(EXEC_DIR)
	cp assets/hippod.service /lib/systemd/system/
	chmod 644 /lib/systemd/system/hippod.service
	@echo "now call systemctl daemon-reload"
	@echo ".. enable service via: systemctl enable hippod.service"
	@echo ".. start service via: systemctl start hippod.service"
	@echo ".. status via: systemctl status hippod.service"
	@echo ".. logging via: journalctl -u hippod.service"

