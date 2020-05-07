import tempfile
import os
import rasa.utils.io as io_utils

from yarl import URL
from typing import List, Text

from rasa.nlu.classifiers.diet_classifier import DIETClassifier
from rasa.nlu.classifiers.embedding_intent_classifier import EmbeddingIntentClassifier
from rasa.nlu.selectors.response_selector import ResponseSelector
from rasa.utils.tensorflow.constants import EPOCHS


def write_temp_file(contents, suffix) -> Text:
    filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + suffix)
    with open(filename, "w+") as f:
        f.write(contents)
        f.flush()
    return filename


def write_file_config(file_config) -> Text:
    return write_temp_file(file_config, "_tmp_config_file.yml")


def latest_request(mocked, request_type, path):
    return mocked.requests.get((request_type, URL(path)))


def json_of_latest_request(r):
    return r[-1].kwargs["json"]


def platform_independent_paths(coll: List[Text]):
    return [i.replace("\\", "/") for i in coll]


def update_number_of_epochs(config_path: Text, output_file: Text):
    config = io_utils.read_yaml_file(config_path)

    if "pipeline" not in config.keys():
        raise ValueError(f"Invalid config provided! File: '{config_path}'.")

    for component in config["pipeline"]:
        # do not update epochs for pipeline templates
        if not isinstance(component, dict):
            continue

        if component["name"] in [
            EmbeddingIntentClassifier.name,
            DIETClassifier.name,
            ResponseSelector.name,
        ]:
            component[EPOCHS] = 1

    io_utils.write_yaml_file(config, output_file)
