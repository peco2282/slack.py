from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx


class HelloWorld(Directive):
    def run(self):
        paragraph_node = nodes.paragraph(text="Hello World!")
        return [paragraph_node]


def setup(app: Sphinx):
    app.add_directive("helloworld", HelloWorld)
