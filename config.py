from yaml import safe_load
from pathlib import Path

with open('config.yaml', 'r') as sec_file:
    config = safe_load(sec_file)

target_page = Path(config["www"]["nerchat_webroot"]).joinpath(config["www"]["page"])
download_basedir = Path(config["www"]["nerchat_webroot"]).joinpath(config["www"]["download"])
