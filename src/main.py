from textnode import TextNode, TextType

def main():
    textnode = TextNode("Here is some example text", TextType.BOLD)
    print(textnode)

if __name__ == "__main__":
    main()