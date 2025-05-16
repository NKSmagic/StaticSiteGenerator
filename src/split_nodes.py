import re
from enum import Enum

from textnode import TextNode, TextType

BlockType = Enum("BlockType", ["PARAGRAPH", "HEADING", "CODE", "QUOTE", "UNORDERED_LIST", "ORDERED_LIST"])

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    result = list()
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            result.append(node)
        elif delimiter not in node.text:
            result.append(node)
        else:
            opening_pos = node.text.find(delimiter)
            if opening_pos != -1:
                closing_pos = node.text.find(delimiter, opening_pos + len(delimiter))
                if closing_pos == -1:
                    raise Exception("No closing delimiter found")
                
                before_text = node.text[:opening_pos]
                inside_text = node.text[opening_pos + len(delimiter):closing_pos]
                after_text = node.text[closing_pos + len(delimiter):]

                before_node = TextNode(before_text, TextType.TEXT)
                inside_node = TextNode(inside_text, text_type)
                after_node = TextNode(after_text, TextType.TEXT)

                result.append(before_node)
                result.append(inside_node)

                if after_node.text.find(delimiter) != -1:
                    result.extend(split_nodes_delimiter([after_node], delimiter, text_type))
                else:
                    result.append(after_node)
    
    return result

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    result = list()
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            result.append(node)
            continue
        
        images = extract_markdown_images(node.text)
        if not images:
            result.append(node)
            continue
        
        image_alt, image_link = images[0]
        split_text = node.text.split(f"![{image_alt}]({image_link})", 1)

        before_text = split_text[0]
        after_text = split_text[1] if len(split_text) > 1 else ""

        if before_text:
            result.append(TextNode(before_text, TextType.TEXT))

        result.append(TextNode(image_alt, TextType.IMAGE, image_link))

        if after_text:
            after_nodes = split_nodes_image([TextNode(after_text, TextType.TEXT)])
            result.extend(after_nodes)   

    return result

def split_nodes_link(old_nodes):
    result = list()

    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            result.append(node)
            continue
        
        links = extract_markdown_links(node.text)
        if not links:
            result.append(node)
            continue
        
        alt_text, link = links[0]
        split_text = node.text.split(f"[{alt_text}]({link})", 1)

        before_text = split_text[0]
        after_text = split_text[1] if len(split_text) > 1 else ""

        if before_text:
            result.append(TextNode(before_text, TextType.TEXT))

        result.append(TextNode(alt_text, TextType.LINK, link))

        if after_text:
            after_nodes = split_nodes_link([TextNode(after_text, TextType.TEXT)])
            result.extend(after_nodes)   

    return result

def text_to_textnodes(text):
    text_list = [TextNode(text, TextType.TEXT)]
    image_passed = split_nodes_image(text_list)
    link_passed = []
    for node in image_passed:
        if node.text_type == TextType.TEXT:
            link_passed.extend(split_nodes_link([node]))
        else:
            link_passed.append(node)
    code_passed = []
    for node in link_passed:
        if node.text_type == TextType.TEXT:
            code_passed.extend(split_nodes_delimiter([node], "`", TextType.CODE))
        else:
            code_passed.append(node)
    bold_passed = []
    for node in code_passed:
        if node.text_type == TextType.TEXT:
            bold_passed.extend(split_nodes_delimiter([node], "**", TextType.BOLD))
        else:
            bold_passed.append(node)
    italic_passed = []
    for node in bold_passed:
        if node.text_type == TextType.TEXT:
            italic_passed.extend(split_nodes_delimiter([node], "_", TextType.ITALIC))
        else:
            italic_passed.append(node)
    return italic_passed
    
def markdown_to_blocks(markdown):
    result = []
    split_text = markdown.split("\n\n")
    for item in split_text:
        if item.strip() != "":
            result.append(item.strip())
    return result

def is_ordered_list(block):
    lines = block.split("\n")
    for i, line in enumerate(lines):
        expected_prefix = f"{i+1}. "
        if not line.startswith(expected_prefix):
            return False
    return True

def block_to_block_type(block):
    if block.startswith("#"):
        count = 0
        for char in block:
            if char == "#":
                count += 1
            else:
                break
        if 1 <= count <= 6 and block[count:count+1] == " ": 
            return BlockType.HEADING
        else:
            return BlockType.PARAGRAPH
    elif block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    elif all(line.startswith("> ") for line in block.split("\n")):
        return BlockType.QUOTE
    elif all(line.startswith("- ") for line in block.split("\n")):
        return BlockType.UNORDERED_LIST
    elif is_ordered_list(block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH