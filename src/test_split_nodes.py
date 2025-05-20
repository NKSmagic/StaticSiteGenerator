import unittest
from textnode import TextNode, TextType
from split_nodes import (
    split_nodes_delimiter, extract_markdown_images, extract_markdown_links, 
    split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks,
    block_to_block_type,markdown_to_html_node, BlockType
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
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    def test_mardown_to_blocks_2(self):
        md = """
This is a _italic_ paragraph

Here starts another paragraph with **bold** text and some piece of 'code'
Here is another line to the same paragraph
And yet another

- This starts a list
- Look! A second Item!
- And another Item
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is a _italic_ paragraph", 
                "Here starts another paragraph with **bold** text and some piece of 'code'\nHere is another line to the same paragraph\nAnd yet another",
                "- This starts a list\n- Look! A second Item!\n- And another Item"
            ]
        )
    
    def test_block_to_block_type(self):
        # Test headings
        assert block_to_block_type("# Heading 1") == BlockType.HEADING
        assert block_to_block_type("## Heading 2") == BlockType.HEADING

        # Test code blocks
        assert block_to_block_type("```\nsome code\n```") == BlockType.CODE
    
        # Test quote blocks
        assert block_to_block_type("> This is a quote") == BlockType.QUOTE
        assert block_to_block_type("> Line 1\n> Line 2") == BlockType.QUOTE

        # Test Unordered List
        assert block_to_block_type("- This is a list\n- A second item") == BlockType.UNORDERED_LIST
        assert block_to_block_type("- One-line list") == BlockType.UNORDERED_LIST

        # Test Orderes List
        assert block_to_block_type("1. This is a ordered list\n2. A second item") == BlockType.ORDERED_LIST

        # Test Paragraph
        assert block_to_block_type("This is a paragraph") == BlockType.PARAGRAPH

        # Test Empty
        assert block_to_block_type("") == BlockType.PARAGRAPH

        # More heading tests
        assert block_to_block_type("### Heading 3") == BlockType.HEADING
        assert block_to_block_type("###### Heading 6") == BlockType.HEADING
        assert block_to_block_type("####### Not a valid heading") == BlockType.PARAGRAPH  # More than 6 # characters

        # More code block tests
        assert block_to_block_type("```python\ndef hello():\n    print('Hello')\n```") == BlockType.CODE
        assert block_to_block_type("```\n```") == BlockType.CODE  # Empty code block

        # Edge cases for quotes
        assert block_to_block_type("> Line 1\n> Line 2\n> Line 3") == BlockType.QUOTE
        assert block_to_block_type(">No space after > character") == BlockType.PARAGRAPH  # Missing space after >

        # More unordered list tests
        assert block_to_block_type("- Item") == BlockType.UNORDERED_LIST  # Single item
        assert block_to_block_type("- Item 1\n- Item 2\n- Item 3") == BlockType.UNORDERED_LIST
        assert block_to_block_type("-Not a list") == BlockType.PARAGRAPH  # Missing space after -

        # More ordered list tests
        assert block_to_block_type("1. Item") == BlockType.ORDERED_LIST  # Single item
        assert block_to_block_type("1. Item 1\n2. Item 2\n3. Item 3") == BlockType.ORDERED_LIST
        assert block_to_block_type("1. Item 1\n3. Item 3") == BlockType.PARAGRAPH  # Missing item 2
        assert block_to_block_type("2. Starting with 2") == BlockType.PARAGRAPH  # Not starting with 1

        # Mixed content tests
        assert block_to_block_type("This is text\nWith multiple lines") == BlockType.PARAGRAPH
        assert block_to_block_type("This has a # in the middle") == BlockType.PARAGRAPH
        assert block_to_block_type("This has\n> a quote line\nbut isn't entirely a quote") == BlockType.PARAGRAPH
    
    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_lists(self):
        md = """
- This is a list
- with items
- and _more_ items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )

    def test_code(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )
        