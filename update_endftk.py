import devtools.build_system as build
from devtools.dependencies import ReleaseDependencies


def main():

    b = build.BuildSystem(
        '../ENDFtk',
        name='ENDFtk'
        )

    b.dependencies = [
        {'name': 'Log', 'tag': 'build/fetchcontent'},
        {'name': 'catch-adapter', 'tag': 'build/fetchcontent'},
        {'name': 'disco', 'tag': 'build/fetchcontent'},
        {'name': 'hana-adapter', 'tag': 'build/fetchcontent'},
        {'name': 'header-utilities', 'tag': 'build/fetchcontent'},
        {'name': 'range-v3-adapter', 'tag': 'build/fetchcontent'}
        ]

    b.write_test_list()
    b.write_cmakelists()
    b.write_dependencies()


def release():

    b = build.BuildSystem(
        '../ENDFtk',
        name='ENDFtk'
        )

    b.dependencies = ReleaseDependencies(
        '../ENDFtk/bin/_deps',
        )

    b.write_dependencies()


if __name__ == '__main__':
    main()
    # release()
