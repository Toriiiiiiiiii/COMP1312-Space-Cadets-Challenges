#!/usr/bin/python3
import requests
import sys
import re

titleRegex = re.compile("<title>(.+)</title>")
descRegex = re.compile("<meta name=\"description\" content=\"(.+)\" />")
schoolRegex = re.compile("<meta name=\"school_metatag\" content=\"(.+)\" />")
facultyRegex = re.compile("<meta name=\"faculty_metatag\" content=\"(.+)\" />")


def getAndDisplayUserInfo(id: str) -> bool:
    response = requests.get(f"https://ecs.soton.ac.uk/people/{id}")
    if response.status_code != 200:
        print(f"ERROR: HTTP status code {response.status_code}")
        return False

    html = str(response.content).replace("\\n", "\n")

    # Instead of searching for potentially re-used class arrangements, use the
    # <title> tag instead.
    # On user pages, the title follows the format of "<name> | University of
    # Southampton".
    title = titleRegex.search(html).group(1)
    name = title.split(" | ")[0]

    # If a user with the specific ID is not found, the website will return
    # the "People" index page instead. Detect this and return an error if user
    # was not found.
    if name == "People":
        return False

    desc = descRegex.search(html).group(1)
    school = schoolRegex.search(html).group(1)
    faculty = facultyRegex.search(html).group(1)

    print(f"# {name}")
    print(f"## University email: {id}@soton.ac.uk")
    print("---")

    print(f"* __Description__: {desc}")
    print(f"* __Faculty__: {faculty}")
    print(f"* __School__: {school}")

    return True


if __name__ == "__main__":
    # The user MUST specify at least 1 ID to search...
    # or else theres no point in even running this program anyway.
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <id1> [id2] [id3] ...")
        exit(1)

    # Put each ID into a list
    ids = sys.argv[1:]

    # Do the thing!!!
    for userID in ids:
        if not getAndDisplayUserInfo(userID):
            # Some simple error checking - Don't continue searching if
            # something went wrong.
            print(f"ERROR: User with ID '{userID}' not found.")
            exit(1)
