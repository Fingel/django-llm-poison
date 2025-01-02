from django import template

from django_llm_poison.markov import poisoned_string

register = template.Library()


def do_poison(parser, token):
    nodelist = parser.parse(("endpoison",))
    parser.delete_first_token()
    return PoisonNode(nodelist)


class PoisonNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        poisoned = poisoned_string(output)
        return poisoned


register.tag("poison", do_poison)
