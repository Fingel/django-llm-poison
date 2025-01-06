import pytest
from django.template.loader import render_to_string

from django_llm_poison.models import MarkovModel
from django_llm_poison.markov import build_model_for_content
from django_llm_poison.templatetags.poison import request_from_bot


@pytest.fixture
def markov_model():
    content = render_to_string("index.html", {})
    return build_model_for_content(content)


@pytest.mark.django_db
def test_models_created(client):
    assert MarkovModel.objects.count() == 0
    response = client.get("/?poison=1")
    assert response.status_code == 200
    assert MarkovModel.objects.count() == 1

    response = client.get("/short/?poison=1")
    assert response.status_code == 200
    assert MarkovModel.objects.count() == 2


@pytest.mark.django_db
def test_posioned_content_served(client, markov_model):
    # Test non-bots get the same content
    response = client.get("/")
    response2 = client.get("/")
    assert response.content == response2.content

    # Test bots get different content
    bot_response = client.get("/?poison=1")
    assert bot_response.content != response.content


def test_user_agent_belongs_to_bot(rf):
    request = rf.get("/", HTTP_USER_AGENT="GPTBot")
    assert request_from_bot(request)

    request = rf.get("/", HTTP_USER_AGENT="Firefox")
    assert not request_from_bot(request)


def test_poison_paramter_acts_like_bot(rf):
    request = rf.get("/?poison=1", HTTP_USER_AGENT="Firefox")
    assert request_from_bot(request)
