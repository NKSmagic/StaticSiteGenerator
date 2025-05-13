import unittest
from textnode import TextNode, TextType
from split_nodes import (
    split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes
)

class TestSplitNodes(unittest.TestCase):
    def test_split_nodes_delimiter_simple(self):
        node = TextNode("This is a text with a `code block` word", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        assert len(result) == 3

        assert result[0].text == "This is a text with a "
        assert result[0].text_type == TextType.TEXT

        assert result[1].text == "code block"
        assert result[1].text_type == TextType.CODE

        assert result[2].text == " word"
        assert result[2].text_type == TextType.TEXT
    
    def test_split_nodes_delimiter_bold(self):
        node = TextNode("This is a text with a **bold** word", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        assert len(result) == 3

        assert result[0].text == "This is a text with a "
        assert result[0].text_type == TextType.TEXT

        assert result[1].text == "bold"
        assert result[1].text_type == TextType.BOLD

        assert result[2].text == " word"
        assert result[2].text_type == TextType.TEXT

    def test_split_nodes_delimiter_italic(self):
        node = TextNode("This is a text with a _italic_ word", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)

        assert len(result) == 3

        assert result[0].text == "This is a text with a "
        assert result[0].text_type == TextType.TEXT

        assert result[1].text == "italic"
        assert result[1].text_type == TextType.ITALIC

        assert result[2].text == " word"
        assert result[2].text_type == TextType.TEXT

    def test_split_nodes_delimiter_multiple(self):
        node = TextNode("This is a text with a **bold** word and another **bold** word", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        assert len(result) == 5

        assert result[0].text == "This is a text with a "
        assert result[0].text_type == TextType.TEXT

        assert result[1].text == "bold"
        assert result[1].text_type == TextType.BOLD

        assert result[2].text == " word and another "
        assert result[2].text_type == TextType.TEXT

        assert result[3].text == "bold"
        assert result[3].text_type == TextType.BOLD

        assert result[4].text == " word"
        assert result[4].text_type == TextType.TEXT

    def test_split_nodes_no_delimiter(self):
        node = TextNode("This is a text without a delimiter", TextType.TEXT)
        result = split_nodes_delimiter([node],"**", TextType.TEXT)

        assert len(result) == 1

        assert result[0].text == "This is a text without a delimiter"
        assert result[0].text_type == TextType.TEXT

    def test_split_nodes_none_text(self):
        node = TextNode("This is a text with a **bold** word", TextType.BOLD)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        assert len(result) == 1

        assert result[0].text == "This is a text with a **bold** word"
        assert result[0].text_type == TextType.BOLD
    
    def test_split_nodes_no_closing_delimiter(self):
        node = TextNode("This is a text without a closing _delimiter", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "_", TextType.TEXT)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
    	    "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_image_single(self):
        node = TextNode(
            "![image](https://www.example.COM/IMAGE.PNG)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://www.example.COM/IMAGE.PNG"),
            ],
            new_nodes,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev) with text that follows",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("another link", TextType.LINK, "https://blog.boot.dev"),
                TextNode(" with text that follows", TextType.TEXT),
            ],
            new_nodes,
        )
        
    def test_text_to_textnodes(self):
        nodes = text_to_textnodes(
            "This is **text** with an _italic_ word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )
