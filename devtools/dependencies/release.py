import os
import subprocess as sp

from .dependency import Dependency
from .dependencies import Dependencies


class ReleaseDependencies(Dependencies):

    def __init__(self, deps_path, dependencies):
        """ Object used to create dependencies for a release based on the
        currently checked out versions of the dependencies.

        Note: this will not pick up any local overrides using cached
        CMake variables (usually through ccmake).

        Parameters
        ----------
        deps_path : str
            The path to FetchContent's collection of repositories, usually
            "_deps" in the build folder.

        dependencies : Dependencies
            The Dependencies constructed from the json file.

        """

        # call parent constructor
        Dependencies.__init__(self)

        toplevel = os.getcwd()
        for dependency in dependencies:
            path = os.path.join(
                deps_path,
                dependency.packageName.lower() + "-src"
                )

            os.chdir(path)

            cmd = ['git', 'rev-parse', 'HEAD']
            p = sp.Popen(cmd, stdout=sp.PIPE)
            commit = p.communicate()[0].decode().strip()
            dependency.tag = commit
            self.add_dependencies(dependency)

            os.chdir(toplevel)

