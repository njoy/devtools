import os
import subprocess as sp

from .dependency import Dependency
from .dependencies import Dependencies


class ReleaseDependencies(Dependencies):

    def __init__(self, path):
        """ Object used to create dependencies for a release based on the
        currently checked out versions of the dependencies.

        Note: this will not pick up any local overrides using cached
        CMake variables (usually through ccmake).

        Parameters
        ----------
        path : str
            The path to FetchContent's collection of repositories, usually
            "_deps" in the build folder.

        """

        # call parent constructor
        Dependencies.__init__(self)

        # automatically add dependencies
        self._register_existing(path)

    ###################################################################
    # Private functions
    ###################################################################

    def _register_existing(self, path):

        toplevel = os.getcwd()
        os.chdir(path)

        for dir_ in sorted(os.listdir(os.getcwd())):
            if not dir_.endswith('-src'):
                continue

            # enter directory
            os.chdir(dir_)

            # name from FetchContent
            # unfortunately, case information is lost
            fname = dir_[:-4]

            # get remote information
            cmd = ['git', 'remote', '-v']
            p = sp.Popen(cmd, stdout=sp.PIPE) 
            remote = p.communicate()[0].decode().strip()
            remote = remote.split()[1]

            # name from remote
            # not always the same as name used in the build system
            rname = remote.split('/')[-1]

            # resolve names
            if fname == rname.lower():
                name = rname
            else:
                name = fname

            # query git tag
            cmd = ['git', 'tag', '--points-at', 'HEAD']
            p = sp.Popen(cmd, stdout=sp.PIPE)
            tag = p.communicate()[0].decode().strip()
            if tag:
                tag = tag.split('\n')[0]

            # query git commit
            cmd = ['git', 'rev-parse', 'HEAD']
            p = sp.Popen(cmd, stdout=sp.PIPE)
            commit = p.communicate()[0].decode().strip()

            # construct commit/tag pair
            if tag:
                commit += ' # tag: {}'.format(tag)

            # register dependency
            dep = Dependency(
                name=name,
                remote=remote,
                tag=commit
                )
            self.add_dependencies(dep)

            # return from directory
            os.chdir('..')

        os.chdir(toplevel)


if __name__ == '__main__':
    d = ReleaseDependencies('../../RECONR/bin/_deps')
    d.cmake_file('blah.cmake')
