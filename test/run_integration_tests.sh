#!/bin/bash

TESTS_DIR=$1

N_TESTS=`ls -d test/integration_tests/*/ | wc -l | xargs`
N_CURRENT=0
N_PASSED=0

for d in ${TESTS_DIR}/*/;
do
    N_CURRENT=`expr ${N_CURRENT} + 1`
    TEST_NAME=`basename ${d}`
    echo -n "Running test ${TEST_NAME} (${N_CURRENT}/${N_TESTS})... "
    ARGS=`cat ${d}/ARGS`

    ORIGINAL=${d}/`cat ${d}/ORIGINAL`
    IMG=${d}/`cat ${d}/IMG`
    if [ ! -f ${IMG} ]; then
        echo -e "\033[31mReference file ${IMG} is missing.\033[0m"
        continue
    fi

    # run script with ARGS to get TEST file
    EXT="${IMG##*.}"
    TEST="${IMG}.test.${EXT}"
    ./pixelsort.py ${ORIGINAL} -o ${TEST} ${ARGS}
    RET_CODE=$?
    # check return code to capture errors
    if [ ${RET_CODE} -ne 0 ]; then
        echo -e "\033[31mCommand \033[0m./pixelsort.py ${ORIGINAL} -o ${TEST} ${ARGS}" \
        "\033[31mfailed with error code ${RET_CODE}.\033[0m"
        continue
    fi

    # check if test file got created before doing `diff`
    if [ ! -f ${TEST} ]; then
        echo -e "\033[31mTest image ${TEST} failed to be created.\033[0m"
        continue
    fi
    # compare test and reference images.
    if [ -z "$(diff ${IMG} ${TEST})" ]; then
        echo -e "\033[32mPASSED.\033[0m"
        rm ${TEST}
        N_PASSED=`expr ${N_PASSED} + 1`
    else
        echo -e "\033[31mFAILED.\033[0m"
    fi
done

echo "Passed ${N_PASSED} / ${N_TESTS} tests."
