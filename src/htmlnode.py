class HTMLNode:
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = [] if children is None else children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if not isinstance(self.props, dict):
            return ""
        else:
            parts = [f' {key}="{value}"' for key, value in self.props.items()]
            return "".join(parts)

    def __repr__(self):
        return f"{self.tag}, {self.value}, {self.children}, {self.props}"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props = None):
        super().__init__(tag, value, None, props)
    
    def to_html(self):
        if self.value == None:
            raise ValueError
        elif self.tag == None:
            return self.value
        elif self.props == None:
            return (f'<{self.tag}>{self.value}</{self.tag}>')
        else:
            prop = super().props_to_html()
            return (f'<{self.tag}{prop}>{self.value}</{self.tag}>')
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
    
    def to_html(self):
        if self.tag == None:
            raise ValueError
        elif self.children == None:
            raise ValueError("No Children")
        elif not self.children:
            return f'<{self.tag}{super().props_to_html()}></{self.tag}>'
        else:
            nodes = f'<{self.tag}{super().props_to_html()}>'
            for child in self.children:
                nodes += f'{child.to_html()}'
            nodes += f'</{self.tag}>'
            return nodes
