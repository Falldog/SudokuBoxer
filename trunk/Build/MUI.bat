SET GETTEXT_DIR=.\gettext
SET MERGE_FLAG=--backup=off --sort-output --no-fuzzy-matching --update
SET PY_LIST_FILE=py_list.txt

python build_util.py  generate_py_list %PY_LIST_FILE%

%GETTEXT_DIR%\xgettext.exe -o "..\lang\base.po"  --files-from=py_list.txt
%GETTEXT_DIR%\msgmerge %MERGE_FLAG% "..\lang\ENU.po" "..\lang\base.po"
%GETTEXT_DIR%\msgmerge %MERGE_FLAG% "..\lang\CHT.po" "..\lang\base.po"
%GETTEXT_DIR%\msgfmt --output-file "..\lang\ENU.mo" "..\lang\ENU.po"
%GETTEXT_DIR%\msgfmt --output-file "..\lang\CHT.mo" "..\lang\CHT.po"

del %PY_LIST_FILE%
del xrc_string.py
