from django import template
import logging
from django_llm_poison.markov import poisoned_string
from django_llm_poison.agents import AGENTS

register = template.Library()
logger = logging.getLogger(__name__)


def request_from_bot(request) -> bool:
    if request.GET.get("poison"):
        return True
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    for agent in AGENTS:
        if agent.lower() in user_agent.lower():
            logger.info("Serving poisoned content to %s", user_agent)
            return True

    return False


def do_poison(parser, token):
    nodelist = parser.parse(("endpoison",))
    parser.delete_first_token()
    return PoisonNode(nodelist)


class PoisonNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        if context.get("request") and request_from_bot(context["request"]):
            return poisoned_string(output)
        else:
            return output


register.tag("poison", do_poison)
