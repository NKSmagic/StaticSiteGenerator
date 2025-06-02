import re
import os
from enum import Enum

from textnode import TextNode, TextType
from htmlnode import HTMLNode, ParentNode, LeafNode
from text_to_html import text_node_to_html_node

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
    elif all(line.startswith(">") for line in block.split("\n")):
        return BlockType.QUOTE
    elif all(line.startswith("- ") for line in block.split("\n")):
        return BlockType.UNORDERED_LIST
    elif is_ordered_list(block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH
    
def text_to_children(text):
    textnodes = text_to_textnodes(text)
    children = []
    for node in textnodes:
        children.append(text_node_to_html_node(node))
    return children

def markdown_to_html_node(markdown):
    blocked = markdown_to_blocks(markdown)
    children = []
    for block in blocked:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return olist_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")

def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)

def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)

def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    text = block[4:-3]
    raw_text_node = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = "<br>".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def extract_title(markdown):
    lines = markdown.splitlines()
    for line in lines:
        if len(line) > 1:
            if line.startswith("#") and line[1] != "#":
                heading = line[1:]
                if heading.strip() == "":
                    raise Exception("No valid h1 header")
                return heading.strip()
    raise Exception("No valid h1 header")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as file:
        content = file.read()
    with open(template_path, "r") as file:
        template = file.read()
    html_content = markdown_to_html_node(content).to_html()
    title = extract_title(content)
    template_title = template.replace("{{ Title }}", title)
    template_content = template_title.replace("{{ Content }}", html_content)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as file:
        file.write(template_content)

def generate_page_recursive(dir_path_content, template_path, dest_dir_path):
    items = os.listdir(dir_path_content)
    for item in items:
        if os.path.isfile(os.path.join(dir_path_content, item)) and item.endswith(".md"):
            html_item = item.replace(".md", ".html")
            generate_page(os.path.join(dir_path_content, item), template_path, os.path.join(dest_dir_path, html_item))
        else:
            os.makedirs(os.path.join(dest_dir_path, item), exist_ok=True)
            generate_page_recursive(os.path.join(dir_path_content, item), template_path, os.path.join(dest_dir_path, item))
