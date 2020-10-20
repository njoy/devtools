import os
from textwrap import dedent


class Dependency:

    def __init__(self,
            name=None,
            remote=None,
            tag=None,
            live_at_head=True):
        """ Container for a dependency.

        """

        # properties
        self._name = name
        self._remote = remote
        self._tag = tag
        self._live_at_head = live_at_head


    ###################################################################
    # Properties
    ###################################################################

    @property
    def name(self):
        """ The name of the repository, as referenced in the build system.

        Typically, this is unnecessary to set, as the name can be implied
        from the remote.  But, for example, the repostiory
        DimensionalAnalysis is named dimwits in the NJOY build system.

        """

        if self._name:
            return self._name
        else:
            return os.path.basename(self.remote)

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def remote(self):
        """ The URL to the remote repository location.

        This is typically a URL to GitHub, but there are of course
        other places one can use.

        If a name is given but not a remote, the NJOY GitHub project
        is assumed to be the location of the repository.  If no name is
        given, a remote must be provided.

        """

        if self._remote:
            return self._remote
        else:
            if not self._name:
                raise Exception(
                    'Dependency must have name and/or remote defined.')
            return 'https://github.com/njoy/{}'.format(self.name)

    @remote.setter
    def remote(self, value: str):
        self._remote = value

    @property
    def tag(self):
        """ The repository tag (i.e., tag, commit hash, or branch name).

        """

        if self.live_at_head:
            if self._tag:
                return 'origin/' + self._tag
            else:
                return 'origin/master'

        else:
            if not self._tag:
                raise Exception(
                    'Dependency must have a tag if not live-at-head.')
            return self._tag

    @tag.setter
    def tag(self, value: str):
        self._tag = value

    @property
    def live_at_head(self):
        """ Flag indicating that a branch rather than a specific commit
        is being followed.

        """

        return self._live_at_head

    @live_at_head.setter
    def live_at_head(self, value: bool):
        self._live_at_head = value


    ###################################################################
    # Public functions
    ###################################################################

    def fetchcontent_declare(self):
        """ Return a string containing the FetchContent_Declare block
        for the dependency.

        """

        result = dedent("""\
            FetchContent_Declare( {name}
                GIT_REPOSITORY  {remote}
                GIT_TAG         {tag}
            """).format(
                name=self.name,
                remote=self.remote,
                tag=self.tag
                )

        if self.live_at_head:
            result += '    GIT_SHALLOW     TRUE\n'

        result += '    )\n'

        return result


if __name__ == '__main__':
    d1 = Dependency(name='foo')
    d2 = Dependency(name='bar', live_at_head=False, tag='v1.0')
    d3 = Dependency(name='bar', live_at_head=False)

    print( d1.fetchcontent_declare() )
    print( d2.fetchcontent_declare() )
    print( d3.fetchcontent_declare() )
