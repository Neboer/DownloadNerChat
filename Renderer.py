from jinja2 import Environment, FileSystemLoader
from FindVersion import RocketChatReleaseDict
from config import config, target_page

env = Environment(loader=FileSystemLoader("templates"))
temp = env.get_template("layout.jinja2")


def render_and_save(template_arguments: RocketChatReleaseDict):
    result = temp.render(template_arguments)
    with open(target_page, 'w', encoding='utf8') as index:
        index.write(result)


if __name__ == "__main__":
    from FindVersion import get_releases

    test_object = get_releases()
    for s in test_object["mobile"].releases:
        test_object["mobile"].releases[s]["download_url"] = "test"

    for s in test_object["desktop"].releases:
        test_object["desktop"].releases[s]["download_url"] = "test"
    render_and_save(test_object)
