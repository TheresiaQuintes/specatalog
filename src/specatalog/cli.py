from pathlib import Path
import json


def print_welcome():
    try:
        from specatalog.main import archive

        if archive.exists(""):
            print(f"""
                  Welcome to specatalog! \n
                  Your archive directory can be found at: \n
                  {archive.archive}\n
                  Have fun!
                  """)
        else:
            raise FileNotFoundError(f"Archive directory not found at {archive.archive}")

    except Exception as e:
        full_message = input(
            "Specatalog could not be loaded! Please run the postinstall first ('specatalog-configuration')\n"
            "If this error persists press 'y' to see the full error message... "
        )
        if full_message == "y":
            print(e)


def configure_defaults():
    # Path to the JSON file
    home_defaults = Path.home() / ".specatalog" / "defaults.json"

    # Step 1: Load existing values from JSON file
    try:
        with home_defaults.open("r") as f:
            result_dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, start with empty values
        result_dict = {
            "remote_archive": False,
            "archive_path": "",
            "host": "",
            "share": "",
            "archive_usr_name": "",
            "archive_password": "",
            "database_url": "",
            "db_usr_name": "",
            "db_password": "",
        }

    # Step 2: Get user input for each key with current values in messages
    # First handle remote_archive since it affects other fields
    current_remote = result_dict.get("remote_archive", False)
    remote_input = input(
        f"Use remote archive? (True/False) [Current: {current_remote}]: "
    ).strip()

    if remote_input.lower() in ["true", "yes", "y"]:
        result_dict["remote_archive"] = True
    elif remote_input.lower() in ["false", "no", "n"]:
        result_dict["remote_archive"] = False
    elif remote_input:  # Non-empty but invalid input
        print(f"Invalid input. Keeping current value: {current_remote}")

    # Now handle other fields based on remote_archive setting
    if not result_dict.get("remote_archive", False):
        # Handle archive_path
        current_path = result_dict.get("archive_path", "")
        path_input = input(f"Enter archive path [Current: {current_path}]: ").strip()
        if path_input:  # Only update if user provided new input
            result_dict["archive_path"] = path_input

    else:
        # Handle host, share, archive_usr_name, archive_password
        fields = [
            ("host", "Enter host name"),
            ("share", "Enter share name"),
            ("archive_usr_name", "Enter archive username"),
            ("archive_password", "Enter archive password"),
        ]

        for field, message in fields:
            current_value = result_dict.get(field, "")
            user_input = input(f"{message} [Current: {current_value}]: ").strip()
            if user_input:  # Only update if user provided new input
                result_dict[field] = user_input

    # Always ask for database fields
    db_fields = [
        ("database_url", "Enter database URL"),
        ("db_usr_name", "Enter database username"),
        ("db_password", "Enter database password"),
    ]

    for field, message in db_fields:
        current_value = result_dict.get(field, "")
        user_input = input(f"{message} [Current: {current_value}]: ").strip()
        if user_input:  # Only update if user provided new input
            result_dict[field] = user_input

    # Step 3: Save the updated configuration to JSON file
    # Ensure the directory exists
    home_defaults.parent.mkdir(parents=True, exist_ok=True)

    # Write the updated configuration
    with home_defaults.open("w") as f:
        json.dump(result_dict, f, indent=2)

    return result_dict
