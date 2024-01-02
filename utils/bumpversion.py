import argparse
from pathlib import Path


class Bumpversion:
    def __init__(self):
        location = Path(__file__)
        version_filename = "version.py"
        self.python_version_file = location.parent.parent / "josh" / version_filename
        self.deploy_version_file = location.parent.parent / "deploy" / "version.txt"

    def update_version(self, part: str = "patch") -> str:
        if part not in ["patch", "minor", "major"]:
            raise ValueError("path: Possible values are: patch, minor, major.")
        old_version = self.get_version()
        version = list(map(int, old_version.split(".")))
        versions = {
            "major": (version[0] + 1, 0, 0),
            "minor": (version[0], version[1] + 1, 0),
            "patch": (version[0], version[1], version[2] + 1),
        }
        new_version = ".".join(map(str, versions[part.lower()]))
        self._write_version(new_version)
        return new_version

    def get_version(self) -> str:
        with self.python_version_file.open() as version_file:
            version = version_file.read().split("=")[1].strip().replace('"', "")
        return version

    def _write_version(self, value: str) -> None:
        with self.python_version_file.open("w") as version_file:
            version_file.write(f'__version__ = "{value}"')
        with self.deploy_version_file.open("w") as version_file:
            version_file.write(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "method",
        help=(
            "Which method should be used. "
            "Possible values are: get_version, update_version."
        ),
    )
    parser.add_argument(
        "--part",
        help="Which part should be updated. Possible values are: patch, minor, major.",
    )
    args = parser.parse_args()
    if args.method not in ["update_version", "get_version"]:
        raise ValueError("method: Possible values are: get_version, update_version.")

    bumpversion = Bumpversion()
    if args.method == "get_version":
        result = bumpversion.get_version()
    else:
        result = bumpversion.update_version(args.part)
    print(result)


if __name__ == "__main__":
    main()
