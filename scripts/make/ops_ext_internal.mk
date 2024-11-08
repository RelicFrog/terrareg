
do-prep-gitleaks:
	@if [ -f "$(GITLEAKS_BINARY)" ]; then \
		echo "Gitleaks binary already exists, skipping preparation."; \
	else \
		echo "prepare gitleaks binary snapshot (v$(GITLEAKS_VERSION)) ..."; \
		ARCH_FOR_GITLEAKS=$(ARCH); \
		if [ "$$ARCH_FOR_GITLEAKS" = "amd64" ]; then ARCH_FOR_GITLEAKS="x64"; fi; \
		echo "gitleaks-source: https://github.com/gitleaks/gitleaks/releases/download/v$(GITLEAKS_VERSION)/gitleaks_$(GITLEAKS_VERSION)_$(OS)_$$ARCH_FOR_GITLEAKS.tar.gz"; \
		mkdir -p $(GITLEAKS_PATH); \
		curl --retry $(CURL_RETRY) --retry-delay $(CURL_RETRY_DELAY) -sSL -o $(GITLEAKS_BINARY).tar.gz https://github.com/gitleaks/gitleaks/releases/download/v$(GITLEAKS_VERSION)/gitleaks_$(GITLEAKS_VERSION)_$(OS)_$$ARCH_FOR_GITLEAKS.tar.gz; \
		tar -xzf $(GITLEAKS_BINARY).tar.gz -C $(GITLEAKS_PATH); \
		chmod +x $(GITLEAKS_BINARY); \
		rm -f $(GITLEAKS_BINARY).tar.gz; \
	fi