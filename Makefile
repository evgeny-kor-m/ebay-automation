PROFILE ?= chrome
# Last run: the most recent RUN_* folder
RUN     ?= $(shell ls -1d reports/RUN_* 2>/dev/null | tail -1)

RESULTS  = $(if $(RUN),$(RUN)/$(PROFILE)/allure-results,reports/allure-results)

.PHONY: unit test test-parallel report report-all

unit:
	pytest tests/unit -q

test:
	pytest tests/e2e --profile $(PROFILE)

test-parallel:
	pytest tests/e2e -n 4 --profile $(PROFILE)

report:            ## Report for a single profile from the last run
	allure serve $(RESULTS)

# report:            ## Report for a single profile from the last run
# 	allure serve $(RUN)/$(PROFILE)/allure-results

report-all:        ## All profiles from the last run in a single report
	allure serve $(RUN)/*/allure-results