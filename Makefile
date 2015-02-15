CORE=core/test_naming.py core/test_timing.py core/test_versioning.py core/test_security.py core/test_interfaces.py
USER=user_supplied/test_user_naming.py user_supplied/test_user_timing.py user_supplied/test_user_security.py
CONFIG_GLOB='heanet.*c.*net$\'
BUILD_TAG?=default
EXECUTABLE=py.test
#EXECUTABLE=nosetests
TEST_OUTPUT=test_results/output-${BUILD_TAG}.xml
all:
	PYTHONPATH=. DIR=heanet SPEC=${CONFIG_GLOB} ${EXECUTABLE} --junitxml ${TEST_OUTPUT}
naming:
	PYTHONPATH=. DIR=heanet SPEC=${CONFIG_GLOB} ${EXECUTABLE} core/test_naming.py --junitxml ${TEST_OUTPUT}
timing:
	PYTHONPATH=. DIR=heanet SPEC=${CONFIG_GLOB} ${EXECUTABLE} core/test_timing.py --junitxml ${TEST_OUTPUT}
security:
	PYTHONPATH=. DIR=heanet SPEC=${CONFIG_GLOB} ${EXECUTABLE} core/test_security.py --junitxml ${TEST_OUTPUT}
heanet-tests:
	PYTHONPATH=. DIR=heanet SPEC=${CONFIG_GLOB} ${EXECUTABLE} ${CORE} ${USER} --junitxml ${TEST_OUTPUT}
