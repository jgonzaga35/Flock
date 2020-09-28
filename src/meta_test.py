import re
import os
import regex

# in english, this regex matches:
#    not a word character or the beginning of the string, followed by
#    the letter d a t a b a s e, followed by
#    not a word character or the end of the string
database_import = re.compile(r'(\W|^)database(\W|$)')

def test_only_blackbox_testing():
    # if this test fails, we are probably importing the database from a test
    # file. We are only supposed to do blackbox testing, so we shouldn't do
    # that. If we aren't, then this test has bug, and you raise an issue on
    # gitlab, and/or have a go at fixing the bug :-)

    # sort to make sure the test always runs in the same order
    for filename in sorted(os.listdir('./src')):
        if filename.endswith('_test.py'):
            line_details = has_database_import('./src/' + filename)
            if line_details is not None:
                line_index, line_content = line_details
                assert False, \
                f"in './src/{filename}', found disallowed database import on line {line_index}: {line_content!r}"

def has_database_import(filename):

    with open(filename) as fp:
        for line_index, line in enumerate(fp):
            assert line != "import database", \
                "should use `from database import ...`, not `import database`"

            if not line.startswith('from database import'):
                continue # skip to next line

            # remove the "from database import" thing
            imported_variables = line[len("from database import"):]

            # make sure we can't find the word "database" in imported_variables
            if database_import.search(imported_variables) is not None:
                return line_index, line