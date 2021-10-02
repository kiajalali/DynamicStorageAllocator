#!/usr//bin/python3
#
# driver.py - The driver tests the correctness
import subprocess
import re
import os
import sys
import argparse
import shutil
import json
# import cryptography

# Basic tests
# The points are per test points. The number of tests that passed or failed directly from C test-suite
tests_json = """{
  "amptjp-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/amptjp-bal.rep": 5
      },
  "cccp-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/cccp-bal.rep": 5
      },
  "cp-decl-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/cp-decl-bal.rep": 5
      },
  "expr-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/expr-bal.rep": 5
      },
  "coalescing-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/coalescing-bal.rep": 5
      },
  "random-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/random-bal.rep": 5
      },
  "random2-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/random2-bal.rep": 5
      },
  "binary-bal.rep": {
      "timeout 60 ./mdriver -V -f traces/binary-bal.rep": 5
      },
  "binary-bal2.rep": {
      "timeout 60 ./mdriver -V -f traces/binary-bal.rep": 5
      },
   "short-malloc_realloc.rep":{
       "timeout 60 ./mdriver-realloc -V -f traces/short-malloc_realloc.rep": 2
   },
   "realloc-bal.rep":{
       "timeout 60 ./mdriver-realloc -V -f traces/realloc-bal.rep": 2
   }  
}
"""


# Points in this case specified by driver2.py
perftests_json = """{
  "Performance": {
      "timeout 60 ./mdriver": 10
      }
    }
"""


Final = {}
Error = ""
Success = ""
PassOrFail = 0
#
# main - Main function
#


def getlines(log, start, end):
    inRecordingMode = False
    for line in log.splitlines():
        if not inRecordingMode:
            if line.startswith(start):
                inRecordingMode = True
        elif line.startswith(end):
            inRecodingMode = False
        else:
            yield(line)


def runtests(test, name):
    total = 0
    points = 0
    global Success
    global Final
    global Error
    global PassOrFail
    for steps in test.keys():
        print(steps)
        p = subprocess.Popen(
            steps, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
        total = total + test[steps]
        # Parse the output
        out_lines = stdout_data.splitlines()
        if p.returncode == 0:
            result_string = list(line for line in getlines(stdout_data.decode(
                'utf-8'), "Results for", "\n"))
            if ("yes" in result_string[1]):
                Success += "#### " + "*"*5+steps+"*"*5
                Success += "\n ```" + stdout_data.decode() + "\n```\n"
                points += test[steps]
            else:
                Error += "#### " + "*"*5+steps+"*"*5
                Error += "\n ```" + stdout_data.decode()
                Error += "\n```\n"
                PassOrFail = 1
        else:
            Error += "#### " + "*"*5+steps+"*"*5
            Error += "\n ```" + stdout_data.decode()
            Error += "\n```\n"
            PassOrFail = p.returncode
        if points < total:
            Final[name.lower()] = {"mark": points,
                                   "comment": "Program exited with error codes"}
        else:
            Final[name.lower()] = {"mark": points,
                                   "comment": "Program ran and output matched.{0}".format(result_string[1])}


def runperftests(test, name):
    total = 0
    points = 0
    global Success
    global Final
    global Error
    global PassOrFail
    for steps in test.keys():
        print(steps)
        p = subprocess.Popen(
            steps, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
        total = total + test[steps]

        # Parse the output
        out_lines = stdout_data.splitlines()
        if p.returncode == 0:
            result_string = list(line for line in getlines(
                stdout_data.decode('utf-8'), "Using default", "\n"))
            if len(result_string) == 1:
                print(result_string)
                calculate = re.search("(\d+)/", result_string[0])
                performance = int(calculate.group(0)[:-1])
                Success += "#### " + "*"*5+steps+"*"*5
                Success += "\n ```" + stdout_data.decode() + "\n```\n"
                points = int(10*(performance/100+0.1))
            else:
                Error += "#### " + "*"*5+steps+"*"*5
                Error += "\n ```" + stdout_data.decode()
                Error += "\n```\n"
                PassOrFail = 1
        else:
            Error += "#### " + "*"*5+steps+"*"*5
            Error += "\n ```" + stdout_data.decode()
            Error += "\n```\n"
            PassOrFail = p.returncode

        if points < total:
            Final[name.lower()] = {"mark": points,
                                   "comment": "Program exited with error codes"}
        else:
            Final[name.lower()] = {"mark": points,
                                   "comment": "Program ran and output matched.{0}".format(result_string[0])}


def main():
        # Parse the command line arguments

    # Basic Tests
    test_dict = json.loads(tests_json)
    for parts in test_dict.keys():
        runtests(test_dict[parts], parts)

    test_dict = json.loads(perftests_json)
    for parts in test_dict.keys():
        runperftests(test_dict[parts], parts)

    githubprefix = os.path.basename(os.getcwd())
    Final["userid"] = "GithubID:" + githubprefix
    j = json.dumps(Final, indent=2)

    with open(githubprefix + "_Grade"+".json", "w+") as text_file:
        text_file.write(j)

    with open("LOG.md", "w+") as text_file:
        text_file.write("## " + '*'*20 + 'FAILED' + '*'*20 + '\n' + Error)
        text_file.write("\n" + "*" * 40)
        text_file.write("\n## " + '*'*20 + 'SUCCESS' + '*'*20 + '\n' + Success)

    sys.exit(PassOrFail)

    # execute main only if called as a script
if __name__ == "__main__":
    main()
