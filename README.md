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

Dependencies can be a string, which is taken as the name of the repository, assumed to be on the NJOY project relative to where the project is hosted and using the default branch.  Otherwise, dependencies can be a dictionary, where more options can be specified.

Dependencies specified as a dictionary must include `"name"` or `"remote"`.  If `"name"` is included without  `"remote"`, the remote is assumed to be `../../njoy/{name}`.  The relative URL capability is provided via [shacl::cmake](https://github.com/shacl/cmake). If only  `"remote"` is specified,  `"name"` is assumed to be the basename of the path.  Both can be included, which is necessary when the basename of the remote does not match the name, e.g. dimwits/DimensionalAnalysis.

Including `"tag"` or `"branch"` is optional, and if neither is provided, it defaults to the master branch.  If both are provided, an error occurs.  This file should include primarily live-at-head dependencies, so specifying a branch is typical.  However, perhaps in the case of a third-party dependency or in an overridden dependency file, a specific Git commit hash or Git tag can be used instead.

## LICENSE
This software is copyrighted by Los Alamos National Laboratory and distributed according to the conditions in the accompanying [LICENSE](LICENSE) file.
