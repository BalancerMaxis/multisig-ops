from .script_utils import get_changed_files, add_extra_payload_data


def main():
    files = get_changed_files()
    add_extra_payload_data(files)


if __name__ == "__main__":
    main()