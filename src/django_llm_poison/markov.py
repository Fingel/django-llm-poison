from django.core.cache import cache
import re
import markovify
import hashlib
from django.utils.html import strip_tags

from markovify.splitters import split_into_sentences
from django_llm_poison.models import MarkovModel


def generate_combined_model():
    combined_model = None
    for model in MarkovModel.objects.all():
        if combined_model is None:
            combined_model = markovify.Text.from_json(model.text)
        else:
            combined_model = markovify.combine(
                [combined_model, markovify.Text.from_json(model.text)]
            )
    return combined_model.compile(inplace=True)


def get_combined_model():
    if not (model := cache.get("combined_model")):
        model = generate_combined_model()
        cache.set("combined_model", model)
    return model


def build_model_for_content(value: str):
    hash = hashlib.sha1(value.encode()).hexdigest()
    stripped = strip_tags(value)
    if not MarkovModel.objects.filter(hash=hash).exists():
        try:
            model = markovify.Text(stripped)
        except Exception:
            return None
        markov_model = MarkovModel.objects.create(hash=hash, text=model.to_json())
        cache.delete("combined_model")
        return markov_model


def poisoned_string(value: str) -> str:
    build_model_for_content(value)
    model = get_combined_model()
    if model is None:
        return value

    sentences = []
    tags = re.split(r"(<[^>]+>)", value)
    for t in tags:
        sentences.extend(split_into_sentences(t))
    for idx, sentence in enumerate(sentences):
        if len(sentence) > 5 and idx != 0 and idx % 3 == 0:
            try:
                generated = model.make_sentence(
                    init_state=tuple(sentence.split()[: model.chain.state_size]),
                    test_output=False,
                )
                sentences[idx] = generated
            except KeyError:
                pass

    return " ".join(sentences)
