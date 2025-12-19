from getpass import getpass
from pathlib import Path
import json

def print_welcome():
    from specatalog.main import BASE_PATH
    print(f"""
          Welcome to specatalog! \n
          Your archive directory can be found at: \n
          {BASE_PATH}\n
          Have fun!
          """)

def configure_db():
    user = input("Choose a username: ")
    pw = getpass("Choose a password: ")
    basepath = Path(input("Choose an absolute path for your archive base: "))
    database_url = input("Enter URL for the database (e.g.localhost:5432/specatalog: " or "localhost:5432/specatalog")
    home_defaults = Path.home() / ".specatalog" / "defaults.json"
    with home_defaults.open("r") as f:
        cfg = json.load(f)
    cfg["usr_name"] = user
    cfg["password"] = pw
    cfg["base_path"] = str(basepath)
    cfg["database_url"] = str(database_url)

    f.close()

    with home_defaults.open("w") as f:
        json.dump(cfg, f, indent=2)

    f.close()
