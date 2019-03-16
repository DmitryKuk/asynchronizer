from argparse import ArgumentParser
from os import environ, stat as stat_fn, unlink
from os.path import abspath, basename, dirname, exists, realpath, splitext
from shutil import rmtree
from stat import S_ISDIR
from subprocess import PIPE, Popen
from sys import argv, executable, exit, stderr
from textwrap import indent


# Parse arguments
parser = ArgumentParser(prog=argv[0], description='MyPy stubgen wrapper')
parser.add_argument(
    '--stubgen', metavar='PATH', type=str, required=True,
    help='MyPy stubgen.py script path to be executed',
)
parser.add_argument('--input', metavar='SO_PATH', type=str, required=True, help='Input .so/.dll file path')
parser.add_argument('--output', metavar='PYI_PATH', type=str, required=True, help='Output .pyi file path')
args = parser.parse_args(argv[1:])


# Remove cached results
try:
    s = stat_fn(args.output)
except FileNotFoundError:
    pass
else:
    if S_ISDIR(s.st_mode):
        rmtree(args.output)
    else:
        unlink(args.output)


# Modify PYTHONPATH to make module visible for stubgen
module_search_path = realpath(dirname(args.input))
python_path = environ.get('PYTHONPATH')
if python_path is None:
    python_path = module_search_path
else:
    python_path = ':'.join(module_search_path, *(p for p in python_path.split(':') if p != module_search_path))

env = {key: value for key, value in environ.items()}
env['PYTHONPATH'] = python_path


# Execute MyPy stubgen with modifed PYTHONPATH and check result
stubgen_process = Popen(
    [
        executable, '-B', '-q', args.stubgen,
        '--output', abspath(dirname(args.output)),
        '-m', splitext(basename(args.input))[0],
    ],
    stdout=PIPE,
    stderr=PIPE,
    env=env,
)
stubgen_stdout, stubgen_stderr = stubgen_process.communicate()


# Print error message, if need
return_code = 0
if not exists(args.output):
    print('Output file not created!', file=stderr)
    return_code = 1

if stubgen_process.returncode != 0:
    return_code = stubgen_process.returncode
    print(f'Stubgen exited with return code {return_code}.', file=stderr)

if return_code != 0:
    if stubgen_stderr:
        print('Stubgen stderr:', file=stderr)
        print(indent(stubgen_stderr.decode(), '    '), file=stderr)

    if stubgen_stdout:
        print('Stubgen stdout:', file=stderr)
        print(indent(stubgen_stdout.decode(), '    '), file=stderr)
