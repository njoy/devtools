import os
import sys
import shutil


class NJOYSourceTree:

    def __init__(self, path):
        """ Object containing information about the source tree for an
        NJOY module.

        Gives access to a list of source files and test directories.

        Currently only supports C++ modules containing cpp and hpp
        files.  Will be extended to support Fortran modules and (once
        a pattern is established) Python bindings.

        """

        # initialize variables
        self._path = path
        self._test_directories = []
        self._compiled_source = []
        self._header_files = []

        # execute functionality
        self._traverse()

    ###################################################################
    # Properties
    ###################################################################

    @property
    def path(self):
        """ The top-level path to the module.  This path should include
        a directory called "src".

        """

        return self._path

    @property
    def header_only(self):
        """ Boolean flag to indicate if the library is header-only.

        Determined by querying the length of the list of compiled source
        files.

        """

        return (len(self._compiled_source) == 0)


    ###################################################################
    # Public functions
    ###################################################################

    def list_compiled_source(self, absolute=False):
        """ Return a list of compiled source files.

        """

        if absolute:
            return self._relative_to_absolute(self._compiled_source)
        else:
            return self._compiled_source

    def list_header_files(self, absolute=False):
        """ Return a list of header files.

        """

        if absolute:
            return self._relative_to_absolute(self._header_files)
        else:
            return self._header_files

    def list_test_directories(self, absolute=False):
        """ Return a list of test directories.

        """

        if absolute:
            return self._relative_to_absolute(self._test_directories)
        else:
            return self._test_directories


    ###################################################################
    # Private functions
    ###################################################################

    def _traverse(self):

        # use os.walk to traverse source tree
        for root, dirs, files in os.walk(os.path.join(self._path, 'src')):

            # find test directories
            for dir_ in dirs:
                if dir_ == 'test':
                    self._test_directories.append(
                        os.path.relpath(
                            os.path.join(root, dir_),
                            start=self._path
                            )
                        )

            # exclude test directories from walk
            dirs[:] = [d for d in dirs if d != 'test']

            # find source/header files
            for file_ in files:
                relpath = os.path.relpath(
                    os.path.join(root, file_),
                    start=self._path
                    )

                if file_.endswith('.cpp'):
                    self._compiled_source.append(relpath)

                elif file_.endswith('.hpp'):
                    self._header_files.append(relpath)

        # sort
        self._header_files.sort()
        self._compiled_source.sort()
        self._test_directories.sort()

    def _relative_to_absolute(self, relpaths):

        convert = lambda x: os.path.abspath(
            os.path.join(self._path, x)
            )

        return [convert(path) for path in relpaths]


if __name__ == '__main__':

    tree = NJOYSourceTree('test_tree')
    for path in tree.list_header_files():
        print( path )
    for path in tree.list_test_directories(absolute=True):
        print( path )
    print( tree.list_compiled_source() )
