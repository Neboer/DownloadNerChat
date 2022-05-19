import re
from datetime import datetime
from typing import TypedDict

from github import Github
from github.GitRelease import GitRelease

from config import config

g = Github(config['github_access_token'])
mobile_repo = g.get_repo('RocketChat/Rocket.Chat.ReactNative')
desktop_repo = g.get_repo('RocketChat/Rocket.Chat.Electron')


class RocketChatAppRelease:
    # version_name: 3.4.10-rc.1
    def __init__(self, version_l: list):
        self.version_l = version_l

    def __gt__(self, other):
        return self.version_l > other.version_l

    def __str__(self):
        return '.'.join(self.version_l)

    def __repr__(self):
        return '.'.join(self.version_l)


class FileAndURL(TypedDict):
    filename: str
    url: str
    download_url: str  # user use this url to access the file downloaded by the server.


class DesktopReleaseFile(TypedDict):
    msi: FileAndURL
    pkg: FileAndURL
    deb: FileAndURL


class MobileReleaseFile(TypedDict):
    apk: FileAndURL
    ipa: FileAndURL


class RocketChatMobileRelease(RocketChatAppRelease):
    def __init__(self, mobile_version: str):
        # Version: 4.27.1
        super().__init__(mobile_version.split('.'))
        self.tag_name = mobile_version
        self.releases: MobileReleaseFile = {}
        self.published_date: datetime = None

    # "https://github.com/RocketChat/Rocket.Chat.Electron/releases/download/3.8.6/rocketchat-3.8.6-mac.pkg"
    @staticmethod
    def from_github_release(rel: GitRelease):
        output = RocketChatMobileRelease(rel.tag_name)
        release_assets = rel.get_assets()
        output.releases = \
            {'apk': next({'filename': i.name, 'url': i.browser_download_url} for i in release_assets if i.name.endswith(".apk")),
             'ipa': next({'filename': i.name, 'url': i.browser_download_url} for i in release_assets if i.name.endswith(".ipa"))}
        output.published_date = rel.published_at
        return output


class RocketChatDesktopRelease(RocketChatAppRelease):
    def __init__(self, desktop_version: str):
        # 3.8.1
        super().__init__(desktop_version.split("."))
        self.tag_name = desktop_version
        self.releases: MobileReleaseFile = {}
        self.published_date: datetime = None

    @staticmethod
    def from_github_release(rel: GitRelease):
        output = RocketChatDesktopRelease(rel.tag_name)
        release_assets = rel.get_assets()
        output.releases = {
            'msi': next({'filename': i.name, 'url': i.browser_download_url} for i in release_assets if i.name.endswith(".msi")),
            'pkg': next({'filename': i.name, 'url': i.browser_download_url} for i in release_assets if i.name.endswith(".pkg")),
            'deb': next({'filename': i.name, 'url': i.browser_download_url} for i in release_assets if i.name.endswith(".deb"))
        }
        output.published_date = rel.published_at
        return output


class RocketChatReleaseDict(TypedDict):
    mobile: RocketChatMobileRelease
    desktop: RocketChatDesktopRelease


def get_config_version() -> RocketChatReleaseDict:
    return {
        'mobile': RocketChatMobileRelease(config['current_versions']['mobile']),
        'desktop': RocketChatDesktopRelease(config['current_versions']['desktop'])
    }


def get_releases() -> RocketChatReleaseDict:
    return {
        'mobile': RocketChatMobileRelease.from_github_release(mobile_repo.get_latest_release()),
        'desktop': RocketChatDesktopRelease.from_github_release(desktop_repo.get_latest_release())
    }


def check_new_version(current_version: RocketChatReleaseDict) -> RocketChatReleaseDict:
    new_version = get_releases()
    compare_result = {}
    if new_version['mobile'].version_l > current_version['mobile'].version_l:
        compare_result['mobile'] = new_version['mobile']
    if new_version['desktop'].version_l > current_version['desktop'].version_l:
        compare_result['desktop'] = new_version['desktop']
    return compare_result
