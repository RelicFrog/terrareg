# Color variables
GREEN = \033[32m
PURPLE = \033[35m
YELLOW = \033[33m
RESET = \033[0m

##-- [ Help + Documentation ] --

## List available tasks on this project
help:
	@echo -e "\n$(GREEN)TerraReg$(RESET) Makefile Context by $(GREEN)Team-42$(RESET)."
	@echo -e "Maintainers: patrick.paechnatz@gmail.com, ..."
	@awk '{ \
			if ($$0 ~ /^.PHONY: [[:alnum:]_.-]+$$/) { \
				helpCommand = substr($$0, index($$0, ":") + 2); \
				if (helpMessage) { \
					printf "$(GREEN)%-10s$(RESET) %s\n", helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^[[:alnum:]_.-]+:/) { \
				helpCommand = substr($$0, 0, index($$0, ":")); \
				if (helpMessage) { \
					printf "$(GREEN)%-22s$(RESET) %s\n", helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^##/) { \
				if (helpMessage) { \
					helpMessage = helpMessage"\n                     "substr($$0, 3); \
				} else { \
					helpMessage = substr($$0, 3); \
				} \
			} else { \
				if (helpMessage) { \
					print "\n$(YELLOW)"helpMessage"$(RESET)\n" ;\
				} \
				helpMessage = ""; \
			} \
		}' \
		$(MAKEFILE_LIST)
