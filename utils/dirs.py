import os
import shutil
import fnmatch
import tempfile

from configuration import Configuration

class TmpDirCopyFilteredWithEnv(tempfile.TemporaryDirectory):

    def __init__(self, dirname):
        self.__configuration = Configuration()
        self.__src_dir = dirname
        # This is bad for single responsability principle, but save
        # some processing time if no dirs are included nor excluded
        if not self.__configuration.include_folders and not self.__configuration.exclude_folders:
            self.__tmp_file_created = False
            self.name = dirname
        else:
            self.__tmp_file_created = True
            super().__init__()
            self.__copy_dirs_filtered()

    def __copy_dirs_filtered(self):
        if self.__configuration.include_folders:
            self.__copy_included_dirs_only()
        else:
            self.__copy_all_tree()

    def __copy_included_dirs_only(self):
        for d in self.__configuration.include_folders:
            src = os.path.join(self.__src_dir, d)
            dst = os.path.join(self.name, d)
            shutil.copytree(src, dst, ignore=self.__ignore_function)

    def __copy_all_tree(self):
        shutil.copytree(self.__src_dir, self.name, ignore=self.__ignore_function,dirs_exist_ok=True)

    def __ignore_function(self, path, names):
        full_names = [os.path.join(path, n) for n in names]
        ignored_full_names = []
        for excluded_dir in self.__configuration.exclude_folders:
            full_excluded_dir = os.path.join(self.__src_dir, excluded_dir)
            ignored_full_names.extend(fnmatch.filter(full_names, full_excluded_dir))
        return [os.path.basename(i) for i in ignored_full_names]
        
    def __exit__(self, exc, value, tb):
        if self.__tmp_file_created:
            super().__exit__(exc, value, tb)