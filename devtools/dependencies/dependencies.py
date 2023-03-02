import os
from textwrap import dedent

from .dependency import Dependency


class Dependencies:

    def __init__(self):
        """ Container for a group of dependencies.

        Used to write out dependency information in build system.

        """

        self._dependencies = []

    ###################################################################
    # Intrinsics
    ###################################################################

    def __len__(self):
        return len(self._dependencies)

    def __iter__(self):
        return self._dependencies.__iter__()

    def __next__(self):
        return self._dependencies.__next__()

    def __bool__(self):
        return len(self._dependencies) > 0

    
    ###################################################################
    # Properties
    ###################################################################

    @property
    def dependencies(self):
        """ List of Dependency objects.

        """

        return self._dependencies

    ###################################################################
    # Public functions
    ##################################################################
    def add_dependencies(self, *args):
        """ Register a dependency with this object.

        """

        for dep in args:
            if not isinstance(dep, Dependency):
                raise Exception(
                    'Cannot register an object other than a Dependency.')
            self._dependencies.append(dep)

    def cmake_file(self, filename, libName):
        """ Write the dependency information to a CMake file.

        """

        f = open(filename, 'w')

        # preamble
        f.write(dedent("""\
            cmake_minimum_required( VERSION 3.24 )
            list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/.cmake)
            include( shacl_FetchContent )

            """)
            )

        # declare dependencies
        f.write(dedent("""\
            #######################################################################
            # Declare project dependencies
            #######################################################################
            
            """)
            )

        for dependency in self.dependencies:
            f.write(dependency.fetchcontent_declare() + '\n')

        # make available
        f.write(dedent("""\
            #######################################################################
            # Load dependencies
            #######################################################################
            
            shacl_FetchContent_MakeAvailable(
            """)
            )
        for dependency in self.dependencies:
            if (dependency.name != "catch-adapter"):
                f.write('    {}\n'.format(dependency.packageName))
        f.write('    )\n\n')

        # Only look for testing library if testing is enabled
        if (any(dependency.name == "catch-adapter" for dependency in self.dependencies)):
            f.write('if (${{{0}_unit_tests}})\n'.format(libName))
            f.write('    shacl_FetchContent_MakeAvailable(catch-adapter)\n')
            f.write('endif()\n\n')

        f.close()

if __name__ == '__main__':
    d1 = Dependency(name='foo')
    d2 = Dependency(name='bar', tag='mybranch')

    d = Dependencies()
    d.add_dependencies(d1, d2)
    d.cmake_file('blah.cmake', 'libraryName')      
