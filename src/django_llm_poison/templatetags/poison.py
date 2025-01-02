from django.core.cache import cache
from django import template
import markovify
import hashlib

from markovify.splitters import split_into_sentences
from django_llm_poison.models import MarkovModel

register = template.Library()


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


@register.filter(is_safe=True)
def poison(value: str):
    hash = hashlib.sha1(value.encode()).hexdigest()
    if not MarkovModel.objects.filter(hash=hash).exists():
        model = markovify.Text(value)
        MarkovModel.objects.create(hash=hash, text=model.to_json())
        cache.delete("combined_model")
    model = get_combined_model()
    if model is None:
        return value

    sentences = split_into_sentences(value)
    for idx, sentence in enumerate(sentences):
        if len(sentence) > 5 and idx > 3 and idx % 3 == 0:
            try:
                generated = model.make_sentence(
                    init_state=tuple(sentence.split()[: model.chain.state_size]),
                    test_output=False,
                )
                sentences[idx] = generated
            except KeyError:
                pass

    return " ".join(sentences)
