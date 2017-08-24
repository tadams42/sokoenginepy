cloc --by-file --skip-uniqueness --quiet src/
cloc --by-file --skip-uniqueness --quiet --not-match-f="autogenerated.*.py" tests
cloc --by-file --skip-uniqueness --quiet lib/libsokoengine --exclude-dir=build --not-match-f="SOK_format_specification.h"
cloc --list-file=bin/cloc_dirs.txt --not-match-f="autogenerated.*.py" --exclude-dir=build -not-match-f="SOK_format_specification.h"
