import os
import shutil
import sys

from textnode import TextNode, TextType
from split_nodes import generate_page_recursive


def copy_directory_contents(source_dir, dest_dir, is_initial_call = True):
    if is_initial_call:
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        os.makedirs(dest_dir)
    static = os.listdir(source_dir)
    for item in static:
        if os.path.isfile(os.path.join(source_dir, item)):
            print(f"Copying file: {os.path.join(source_dir, item)}")
            shutil.copy(os.path.join(source_dir, item), os.path.join(dest_dir, item))
        else:
            os.makedirs(os.path.join(dest_dir, item))
            copy_directory_contents(os.path.join(source_dir, item), os.path.join(dest_dir, item), False)

def main():
    copy_directory_contents("./static", "./docs")
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    generate_page_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()