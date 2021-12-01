#!/bin/bash

non_zero=0

function run_multiline_cmd_with_check() {
  bash -c "$@"
  if [[ $? -ne 0 ]] 
  then
    printf "failed"
    ((non_zero++))
  fi
}

function run_cmd_with_check() {
  "$@"
  if [[ $? -ne 0 ]] 
  then
    printf "failed"
    ((non_zero++))
  fi
}

REPO=$PWD
# Build malloc driver
run_cmd_with_check make mdriver
run_cmd_with_check make mdriver-realloc
run_cmd_with_check python3 driver.py 
cat LOG.md >> LOG

exit ${non_zero}
