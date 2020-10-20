import os
from textwrap import dedent

from .njoy_source_tree import NJOYSourceTree
from .dependencies import Dependency, Dependencies, ReleaseDependencies


class BuildSystem:

    def __init__(self, path, name=None):
        """ Object controlling the writing of build system files.

        Currently only supports C++ modules containing cpp and hpp
        files.  Will be extended to support Fortran modules and (once
        a pattern is established) Python bindings.

        """

        # initialize variables
        self._path = path
        self._name = name

        # source tree
        self._tree = NJOYSourceTree(self.path)

        # dependencies
        self._dependencies = Dependencies()

        # options
        self.logging = True
        self.executable = False


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
    def name(self):
        """ The name of the repository, derived from the basename of the
        path.

        """

        if self._name:
            return self._name
        else:
            return os.path.basename(self._path)

    @property
    def dependencies(self):
        """ List of dependencies.

        """

        return self._dependencies

    @dependencies.setter
    def dependencies(self, value):
        if isinstance(value, Dependencies):
            self._dependencies = value

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    self._dependencies.add_dependencies(
                        Dependency(name=item)
                        )
                elif isinstance(item, dict):
                    self._dependencies.add_dependencies(
                        Dependency(**item)
                        )
                else:
                    raise Exception('%r is an invalid dependency.' % item)


    ###################################################################
    # Public functions
    ###################################################################

    def write_test_directories(self):
        """ Write the CMakeLists.txt file for each test directory.

        """

        # setup
        test_directories = self._tree.list_test_directories()

        # loop over all test directories
        for dir_ in test_directories:

            # write CMakeLists.txt for directory
            self._one_test( dir_ )


    def write_test_list(self):
        """ Write the unit_testing.cmake file for the repository.

        """

        # setup
        test_directories = self._tree.list_test_directories()
        self._cmake_directory()

        # filename to write output
        filename = os.path.join(
            self._path,
            'cmake',
            'unit_testing.cmake'
            )

        # create CMake file
        with open(filename, 'w') as f:

            f.write(dedent("""\
                #######################################################################
                # Setup
                #######################################################################

                message( STATUS "Adding {} unit testing" )
                enable_testing()


                #######################################################################
                # Unit testing directories
                #######################################################################

                """.format(self.name))
                )

            for dir_ in test_directories:
                f.write('add_subdirectory( {} )\n'.format(dir_))

    def write_cmakelists(self):
        """ Write the CMakeLists.txt file for the project.

        """

        # filename to write output
        filename = os.path.join(
            self._path,
            'CMakeLists.txt'
            )
        f = open(filename, 'w')

        # preamble, setup
        f.write(dedent("""\
            ########################################################################
            # Preamble
            ########################################################################
            
            cmake_minimum_required( VERSION 3.14 )
            project( {0} LANGUAGES CXX )
            
            
            ########################################################################
            # Project-wide setup
            ########################################################################
            
            set( CMAKE_CXX_STANDARD 17 )
            set( CMAKE_CXX_STANDARD_REQUIRED YES )
            
            option( {0}_unit_tests
                "Compile the {0} unit tests and integrate with ctest" ON
                )
            option( strict_compile
                "Treat all warnings as errors." ON
                )
            
            # Compile flags
            set( common_flags "-Wall" "-Wextra" "-Wpedantic" )
            set( strict_flags "-Werror" )
            set( release_flags "-O3" )
            set( debug_flags "-O0" "-g" )

            
            """.format(self.name))
            )

        # dependencies
        print( self.dependencies, len(self.dependencies) )
        if self.dependencies:
            f.write(dedent("""\
                ########################################################################
                # Dependencies
                ########################################################################
                
                set( REPOSITORIES "release"
                    CACHE STRING
                    "Options for where to fetch repositories: develop, release, local"
                    )
                
                if( REPOSITORIES STREQUAL "develop" )
                    include( cmake/develop_dependencies.cmake )
                
                elseif( REPOSITORIES STREQUAL "release" )
                    include( cmake/release_dependencies.cmake )
                
                elseif( REPOSITORIES STREQUAL "local" )
                    include( cmake/local_dependencies.cmake )
                
                endif()
                
                
                """.format(self.name))
                )

        # project targets
        f.write(dedent("""\
            ########################################################################
            # Project targets
            ########################################################################
                
            """)
            )

        if self._tree.header_only:
            link_type = 'INTERFACE'
        else:
            link_type = 'PUBLIC'

        if self.executable:
            f.write('add_executable( {} '.format(self.name))
        else:
            f.write('add_library( {} '.format(self.name))

        if self._tree.header_only:
            f.write('INTERFACE')
        else:
            for file_ in self._tree.list_compiled_source():
                f.write('\n    {}'.format(file_))
        f.write('\n    )\n')

        f.write(
            'target_include_directories( {0} {1} src/ )\n'
            ''.format(self.name, link_type)
            )

        if self.dependencies:
            f.write('target_link_libraries( {}\n'.format(self.name))
            for d in self.dependencies:
                f.write('    {0} {1}\n'.format(link_type, d.name))
            f.write('    )\n')

        if not self._tree.header_only:
            f.write(dedent("""\
                target_compile_options( {} PRIVATE
                    ${{common_flags}}
                    $<$<BOOL:${{strict_compile}}>:${{strict_flags}}>
                    $<$<CONFIG:DEBUG>:${{debug_flags}}>
                    $<$<CONFIG:RELEASE>:${{release_flags}}>
                    )
                """.format(self.name))
                )

        f.write('\n\n')

        # top level only
        f.write(dedent("""\
            #######################################################################
            # Top-level Only
            #######################################################################
            
            if( CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR )
            
                # unit testing
                if( {}_unit_tests )
                    include( cmake/unit_testing.cmake )
                endif()
            
            endif()
            """.format(self.name))
            )

        # close file
        f.close()

        # report completion
        if self.logging:
            print( 'Wrote CMakeLists.txt.' )

    def write_dependencies(self):
        """ Write Dependencies CMake file.  Location depends on
        type of dependencies given.

        """

        # setup
        self._cmake_directory()

        if isinstance(self.dependencies, ReleaseDependencies):
            filename = 'release_dependencies.cmake'
        else:
            filename = 'develop_dependencies.cmake'

        self.dependencies.cmake_file(
            os.path.join(
                self._path,
                'cmake',
                filename
                )
            )


    ###################################################################
    # Private functions
    ###################################################################

    def _cmake_directory(self):
        """ Create cmake directory if it doesn't already exist.

        """

        dir_ = os.path.join(
            self._path,
            'cmake'
            )

        if not os.path.isdir(dir_):
            os.mkdir(dir_)

    def _one_test(self, dir_):
        """ Write CMakeLists.txt for one test directory.

        """

        # filename to write output
        filename = os.path.join(
            self._path,
            dir_,
            'CMakeLists.txt'
            )

        # test name
        testname = dir_.split('/')[-2]

        # write CMakeLists.txt
        with open(filename, 'w') as f:

            # preamble
            f.write(dedent("""\
                set( CMAKE_CXX_STANDARD 17 )
                set( CMAKE_CXX_STANDARD_REQUIRED YES )

                """)
                )

            # first line
            f.write('add_executable( {}.test\n'.format(testname))

            # full relative path to dir_
            dirname = os.path.join(
                self.path,
                dir_
                )

            # files
            for file_ in os.listdir(dirname):

                # full relative path to file_
                fname = os.path.join(
                    dirname,
                    file_
                    )

                # skip anything not a cpp
                if not os.path.isfile(fname):
                    continue
                elif not fname.endswith('.cpp'):
                    continue

                # list files
                f.write('    {}\n'.format(file_))

            f.write('    )\n')

            # link libraries
            f.write(dedent("""\
                target_link_libraries( {0}.test
                    PUBLIC {1}
                    )
                """.format(testname, self.name))
                )
    
            # compile options
            f.write(dedent("""\
                target_compile_options( {}.test PRIVATE
                    ${{common_flags}}
                    $<$<BOOL:${{strict_compile}}>:${{strict_flags}}>
                    $<$<CONFIG:DEBUG>:${{debug_flags}}>
                    $<$<CONFIG:RELEASE>:${{release_flags}}>
                    )
                """.format(testname))
                )

            # add test
            f.write(dedent("""\
                add_test(
                    NAME {0}
                    COMMAND {0}.test
                    )
                """.format(testname))
                )

        # record completion
        if self.logging:
            print( 'Wrote CMakeLists.txt for {} test directory.'
                   ''.format(dir_) )


if __name__ == '__main__':
    b = BuildSystem('test_tree')
    b.write_test_list()
    b.write_test_directories()
    b.dependencies = ['zlo']
    b.dependencies.add_dependencies(
        Dependency(name='baz'),
        Dependency(name='fiz')
        )
    b.write_cmakelists()
    b.write_dependencies()
