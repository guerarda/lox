# Define the test directory path
TESTS_DIR := tests
TESTCASES_DIR := $(TESTS_DIR)/cases
BUILD_DIR := build

.PHONY: test clean

# Main test target with conditional args
test: $(BUILD_DIR)/tests.py
	@ # Get all args after "test"
	@$(eval EXTRA_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)))
	@ # If there are extra args, don't use the --skip defaults
	$(if $(EXTRA_ARGS), \
		python -m $(TESTS_DIR).loxtest -v run $(EXTRA_ARGS), \
		python -m $(TESTS_DIR).loxtest -v run --skip EarlyChapters Limits\
	)

$(BUILD_DIR)/tests.py: $(TESTS_DIR)/loxtest.py
	@mkdir -p $(BUILD_DIR)
	@touch $(BUILD_DIR)/__init__.py
	python -m $(TESTS_DIR).loxtest generate $(TESTCASES_DIR) --out $(BUILD_DIR)/tests.py

# Clean target to remove generated test file
clean:
	rm -f $(BUILD_DIR)/tests.py

# This rule matches any extra arguments so make
# doesn't complain about no rule to make target
%:
	@:
