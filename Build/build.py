#!/usr/bin/env python
# @author: Falldog
#

import os
import shutil
import argparse
import subprocess
import build_util
from os.path import join, dirname, abspath

CUR_DIR = abspath(dirname(__file__))
ROOT_DIR = abspath(join(CUR_DIR, '..'))
DIST_DIR = join(CUR_DIR, 'dist')
PUZZLE_DIR = join(CUR_DIR, 'puzzle')
GETTEXT_DIR = join(CUR_DIR, 'gettext')
VERSION_PATH = join(ROOT_DIR, 'version')
LANG_DIR = join(ROOT_DIR, 'lang')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-po', dest='update_po', default=False, action='store_true',
                        help='update language translating PO file')
    args = parser.parse_args()
    return args


class Builder():
    def __init__(self):
        self.ver_date = build_util.GenerateVersion(VERSION_PATH)
        self.dist_dir = join(DIST_DIR, 'SudokuBoxer-%s' % self.ver_date)
        self.puzzle_dir = join(self.dist_dir, 'puzzle')
        self.lang_dir = join(self.dist_dir, 'lang')

        if not os.path.isdir(DIST_DIR):
            os.mkdir(DIST_DIR)
        if os.path.isdir(self.dist_dir):
            shutil.rmtree(self.dist_dir)
        if os.path.isdir(join(DIST_DIR, 'SudokuBoxer')):
            shutil.rmtree(join(DIST_DIR, 'SudokuBoxer'))

    def build(self):
        self.update_MUI_mo()
        self.process_pyinstaller()
        self.copy_resource()

    def update_MUI_po(self):
        ''' update PO file for translating it '''
        py_list_path = 'py_list.txt'
        msgmerge_flags = '--backup=off --sort-output --no-fuzzy-matching --update'
        build_util.GeneratePyList(py_list_path)

        subprocess.check_call('%s -o "%s" --files-from=%s' % (join(GETTEXT_DIR, 'xgettext.exe'),
                                                              join(LANG_DIR, 'base.po'),
                                                              py_list_path),
                              shell=True)
        subprocess.check_call('%s %s "%s" "%s"' % (join(GETTEXT_DIR, 'msgmerge'), msgmerge_flags,
                                                   join(LANG_DIR, 'ENU.po'), join(LANG_DIR, 'base.po')),
                              shell=True)
        subprocess.check_call('%s %s "%s" "%s"' % (join(GETTEXT_DIR, 'msgmerge'), msgmerge_flags,
                                                   join(LANG_DIR, 'CHT.po'), join(LANG_DIR, 'base.po')),
                              shell=True)
        os.remove(py_list_path)

    def update_MUI_mo(self):
        ''' convert .po(TEXT file) to .mo(Binary file) '''
        msgmerge_output_flags = '--output-file'
        subprocess.check_call('%s %s "%s" "%s"' % (join(GETTEXT_DIR, 'msgfmt'), msgmerge_output_flags,
                                                   join(LANG_DIR, 'CHT.mo'), join(LANG_DIR, 'CHT.po')),
                              shell=True)
        subprocess.check_call('%s %s "%s" "%s"' % (join(GETTEXT_DIR, 'msgfmt'), msgmerge_output_flags,
                                                   join(LANG_DIR, 'ENU.mo'), join(LANG_DIR, 'ENU.po')),
                              shell=True)

    def process_pyinstaller(self):
        cwd = os.getcwd()
        os.chdir(CUR_DIR)
        try:
            subprocess.check_call(['pyinstaller', 'SudokuBoxer.spec'])

            # rename to SudokuBoxer-[version]
            ori_dist_dir = join(DIST_DIR, 'SudokuBoxer')
            if os.path.exists(ori_dist_dir):
                os.rename(ori_dist_dir, self.dist_dir)

        finally:
            os.chdir(cwd)

    def copy_resource(self):
        shutil.copyfile(join(ROOT_DIR, 'version'), join(self.dist_dir, 'version'))

        os.mkdir(self.puzzle_dir)
        shutil.copyfile(join(ROOT_DIR, 'puzzle', 'PuzzleDB-1000'), join(self.puzzle_dir, 'PuzzleDB'))

        shutil.copytree(join(ROOT_DIR, 'img'), join(self.dist_dir, 'img'))

        self.lang_dir = join(self.dist_dir, 'lang')
        os.mkdir(self.lang_dir)
        for f in os.listdir(join(ROOT_DIR, 'lang')):
            if os.path.splitext(f)[1] == '.mo':
                shutil.copyfile(join(ROOT_DIR, 'lang', f), join(self.lang_dir, f))


if __name__ == '__main__':
    args = parse_args()
    builder = Builder()
    if args.update_po:
        builder.update_MUI_po()
    else:
        builder.build()
