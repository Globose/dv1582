
import os
import sys
import logging
import pylint.lint


LOG_LEVEL = 'INFO'
LINT_THRESHOLD = 8.0
INITIAL_TIME_LIMIT = 0.5

# Get the current working directory
current_directory = os.getcwd()

# List to store all file paths and names
file_paths = []

# Walk through the directory and its subdirectories and get all file paths and names
for foldername, _, filenames in os.walk(current_directory):
    subfolders = '\\'.join(foldername.split(
        "\\")[len(current_directory.split("\\")):])

    for filename in filenames:
        # Get the full file path
        file_path = os.path.join(subfolders, filename)

        # Add the file path and name to the list
        if filename != __file__:
            file_paths.append(file_path)

FILES = file_paths


def check_code_quality():
    print(
        f'\nChecking code quality by pylint score, {LINT_THRESHOLD} is minimum to pass ...')
    log.info(
        'Checking code quality by pylint score, %s is minimum to pass', LINT_THRESHOLD)
    stdout = sys.stdout
    outfile = open('pylint_report.txt', 'w', encoding="UTF-8")

    sys.stdout = outfile
    run = pylint.lint.Run(
        FILES, exit=False)
    try:    # Linting for Codegrades python version (3.6)
        score = run.linter.stats['global_note']
    except:  # Linting for my python version (3.10)
        score = run.linter.stats.global_note
    if score < LINT_THRESHOLD:
        log.info(
            'The pylint score is only %s,at least %s required', score, LINT_THRESHOLD)
        sys.stdout = stdout
        outfile.close()
        print(
            f'  Test failed!\nThe pylint score is only {score:.2f}, ' +
            f'  at least {LINT_THRESHOLD} required')
        print('Detailed report can be viewed in pylint_report.txt\n')
        log.info('Detailed report can be viewed in pylint_report.txt\n')
        sys.exit(1)
    else:
        sys.stdout = stdout
        print(f'  Lint score is {score:.2f}')
        log.info('  Lint score is %s', score)
    print('Lint score OK!\nDetailed lint report can be viewed in pylint_report.txt\n')
    log.info('Lint score OK!\nDetailed lint report can be viewed in pylint_report.txt')


if __name__ == '__main__':
    log = logging.getLogger(__name__)
    logging.basicConfig(filename=current_directory+'/test.log',
                        level=os.environ.get('LOGLEVEL', LOG_LEVEL),
                        filemode='w',
                        format='\n%(levelname)-4s [L:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S')

    check_code_quality()
