# 目录结构：
# file_root/
#   mobile/
#       Version: 4.27.1/
#           android-official-release.apk
#           ios-official-release.ipa
#   desktop/
#       3.8.6/
#           rocketchat-3.8.6-win-x64.msi
#           rocketchat-3.8.6-mac.pkg
#           rocketchat-3.8.6-linux-amd64.deb
from typing import Union
from os import makedirs
from pathlib import Path

from requests import get
from time import sleep
from config import config
from urllib.parse import urljoin, quote

from FindVersion import get_config_version, check_new_version, RocketChatDesktopRelease, RocketChatMobileRelease, \
    FileAndURL
from Renderer import render_and_save
from github import GithubException
import logging

logging.basicConfig(filename=config["log_file"], encoding='utf-8', level=logging.INFO)


# direct download a url to a specific file location
def direct_download(target_file_location: Path, url: str):
    with get(url, stream=True) as r:
        r.raise_for_status()
        with open(target_file_location, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


# combine the FindVersion
def loop_check_and_download():
    current_versions = get_config_version()
    while True:
        try:
            check_result = check_new_version(current_versions)
            if check_result != {}:
                logging.info(f"发现新版本{check_result}")
                for device_name in check_result:
                    release: Union[RocketChatDesktopRelease, RocketChatMobileRelease] = check_result[device_name]
                    # folder: download/mobile/3.3.0, 3.3.0是stringify的结果
                    # device_name: mobile desktop
                    # download folder must not start with slash /
                    relative_base_download_url = urljoin(config["www"]["download"] + '/', device_name + "/" + str(release))
                    # r_b_d_u: download/mobile/3.3.0
                    for asset_filetype in release.releases:
                        current_asset_file: FileAndURL = release.releases[asset_filetype]
                        absolute_folder_location = Path(config["www"]["nerchat_webroot"]).joinpath(relative_base_download_url)
                        makedirs(absolute_folder_location, exist_ok=True)
                        absolute_file_location = absolute_folder_location.joinpath(current_asset_file['filename'])
                        logging.info(f"开始下载{absolute_file_location}")
                        # 使用代理 https://ghproxy.com/
                        direct_download(absolute_file_location, "https://ghproxy.com/" + current_asset_file['url'])
                        logging.info("下载完成")
                        current_asset_file['download_url'] = quote(urljoin(relative_base_download_url+"/", current_asset_file['filename']))
                current_versions.update(check_result)
                logging.info("更新页面")
                render_and_save(current_versions)
        except GithubException as ge:
            logging.exception(ge)
        sleep(config['timeout_s'])


if __name__ == "__main__":
    loop_check_and_download()
