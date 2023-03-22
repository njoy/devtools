# system imports
import argparse
import json
import os

# local imports
import devtools.build_system as build
from devtools.dependencies import ReleaseDependencies, Dependency


def main():

    # parse input arguments
    args = process_input()

    # make the build system
    make_build_system(args)


def process_input():
    """ Use argparse for command line input processing.

    """

    parser = argparse.ArgumentParser(
        description='Update build system for a given repository '
                    'in the NJOY framework.'
        )

    # required input
    parser.add_argument(
        'path',
        type=str,
        help='path to repository'
        )

    # optional inputs
    parser.add_argument(
        '--name', '-n',
        type=str,
        help='repository name',
        default=None
        )
    parser.add_argument(
        '--dependencies', '-d',
        type=str,
        help='dependency file',
        default='dependencies.json'
        )
    parser.add_argument(
        '--build-dir', '-b',
        type=str,
        help='build directory (relative to path)',
        default='bin'
        )
    parser.add_argument(
        '--default-branch',
        type=str,
        help='default branch to use for live-at-head dependencies',
        default='master'
        )

    # exclusive group
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '--develop',
        action='store_false',
        dest='release',
        help='Create develop_dependencies.cmake file (default)',
        default=False
        )    
    group.add_argument(
        '--release',
        action='store_true',
        dest='release',
        help='Create release_dependencies.cmake file'
        )    

    # parse and return
    args = parser.parse_args()
    return args


def make_build_system(args):

    Dependency.default_branch = args.default_branch

    b = build.BuildSystem(
        args.path,
        args.name
        ) 


    # Dependencies are given in an input JSON file
    with open(args.dependencies, 'r') as f:
        dependencies = json.load(f)

    deps = dependencies[b.name]
    if deps:
        b.dependencies = deps

    if args.release:
        # Release dependencies are the same as the develop dependencies
        # but with the hashes taken from examining the
        # checked-out hash in the build/_deps folder 
        deps_path = os.path.join(
            args.path,
            args.build_dir,
            '_deps'
            )
        b.dependencies = ReleaseDependencies(deps_path)



    b.write_dependencies()
    if not args.release:
        b.write_installation_dependencies()
        b.write_cmakelists()
        b.write_test_list()


if __name__ == '__main__':
    main()
