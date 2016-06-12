#!/bin/bash

usage() { echo "Usage: $0 -p <pixelsort script> tests..." 1>&2; exit 1; }

# when user presses Ctrl-C, stop tests and return to initial dir
INITIAL_DIR=${PWD}
trap ctrl_c INT
ctrl_c() {
    echo "Test suite interrupted. Passed ${N_PASSED} / ${N_TESTS} tests."
    cd ${INITIAL_DIR}
    exit 1
}

# process command line args
while getopts ":p:" opt; do
    case ${opt} in
        p)
            PIXELSORT_PATH=${OPTARG}
            ;;
        \?)
            echo "Invalid option: -${OPTARG}" >&2
            usage
            ;;
        :)
            echo "OPTION -${OPTARG} requires an argument." >&2
            usage
            ;;
        *)
            usage
            ;;
    esac
done

# get absolute path of pixelsorting script
if [ -z ${PIXELSORT_PATH} ]; then
    echo "pixelsort script path not specified." >&2
    usage
fi
PIXELSORT_PATH=${PWD}/${PIXELSORT_PATH}

shift $((OPTIND-1))
TESTS=$@
N_TESTS=$#
N_CURRENT=0
N_PASSED=0

for d in ${TESTS};
do
    # run script in the test directory in case arguments refer to local files (e.g. image-mask.jpg)
    pushd ${d} > /dev/null

    N_CURRENT=`expr ${N_CURRENT} + 1`
    TEST_NAME=`basename ${d}`
    echo -n "Running test ${TEST_NAME} (${N_CURRENT}/${N_TESTS})... "
    ARGS=`cat ARGS`

    ORIGINAL=`cat ORIGINAL`
    IMG=`cat IMG`
    if [ ! -f ${IMG} ]; then
        echo -e "\033[31mReference file ${IMG} is missing.\033[0m"
        popd > /dev/null
        continue
    fi

    # run script with ARGS to get TEST file
    EXT="${IMG##*.}"
    TEST="${IMG}.test.${EXT}"
    eval ${PIXELSORT_PATH} ${ORIGINAL} -o ${TEST} ${ARGS}
    RET_CODE=$?
    # check return code to capture errors
    if [ ${RET_CODE} -ne 0 ]; then
        echo -e "\033[31mCommand \033[0m${PIXELSORT_PATH} ${ORIGINAL} -o ${TEST} ${ARGS}" \
        "\033[31mfailed with error code ${RET_CODE}.\033[0m"
        popd > /dev/null
        continue
    fi

    # check if test file got created before doing `diff`
    if [ ! -f ${TEST} ]; then
        echo -e "\033[31mTest image ${TEST} failed to be created.\033[0m"
        popd > /dev/null
        continue
    fi
    # compare test and reference images.
    if [ -z "$(diff ${IMG} ${TEST})" ]; then
        echo -e "\033[32mPASSED.\033[0m"
        rm ${TEST}
        N_PASSED=`expr ${N_PASSED} + 1`
    else
        # Don't delete temp file when a test fails, for debugging purposes.
        echo -e "\033[31mFAILED.\033[0m"
    fi

    popd > /dev/null
done

echo "Passed ${N_PASSED} / ${N_TESTS} tests."
