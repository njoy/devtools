# devtools

## Basic usage

The build system is constructed by invoking:
`python update_repositories.py /path/to/repository`
This script takes a variety of command line arguments, which can be found by using the `-h` or `--help` flag.

The script can be executed in one of two modes: develop (default) and release.  Develop will create the build system and include a `develop_dependencies.cmake` file, which typically uses the live-at-head paradigm.  Release requires the build system already be present and the `_deps` folder populated in the repository's build directory.  It creates the `release_dependencies.cmake` file, which specifies Git commit hashes rather than branches.

Dependencies used are specified in the `dependencies.json` files, although this file can be overridden at the command line.


## Dependency specifications
Each supported component's list of dependencies is included in the `dependencies.json` file.  Additional components can be added to this list or a user can override the file at the command line.

The JSON file requires an entry with the same name as the component, as specified on the command line or inferred from the path.  That entry should have a list of dictionaries, each representing a dependency.

Dependencies must specify `"name"` or `"remote"`.  If `"name"` is specified without  `"remote"`, the remote is assumed to be `https://github.com/njoy/{name}`.  If only  `"remote"` is specified,  `"name"` is assumed to be the basename of the path.  Both can be specified, which is necessary when the basename of the remote does not match the name, e.g. dimwits/DimensionalAnalysis.

Specifying `"tag"` is optional, and it defaults to the master branch.  This file should include primarily live-at-head dependencies, so specifying a branch is typical.  However, perhaps in the case of a third-party dependency or in an overridden dependency file, a specific Git commit hash or Git tag can be used instead.  In this case, `"live_at_head": False` should be included in the dependency's dictionary.


## LICENSE
This software is copyrighted by Los Alamos National Laboratory and distributed according to the conditions in the accompanying [LICENSE](LICENSE) file.
