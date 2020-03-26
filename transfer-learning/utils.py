from datetime import datetime
import json
import logging
import os
import tarfile
import tempfile
import socket
import pdb
import pandas
import numpy as np
import torch

from transformers import cached_path

HUGGINGFACE_MODEL = "https://s3.amazonaws.com/models.huggingface.co/transfer-learning-chatbot/gpt_personachat_cache.tar.gz"
LYRICS_DATA = "/Users/nikhil.phatak/my/nlp-project/data/lyrics.csv"


def download_pretrained_model():
    resolved_archive_file = cached_path(HUGGINGFACE_MODEL)
    tempdir = tempfile.mkdtemp()
    with tarfile.open(resolved_archive_file, 'r:gz') as archive:
        archive.extractall(tempdir)
    return tempdir


def parse_dataframe(df):
    output = []
    for artist in df["artist"].unique():
        current_rows = df.loc[df["artist"] == artist]
        current_lyrics = []
        for _, row in current_rows.iterrows():
            lyr = row["lyrics"]
            if lyr:
                current_lyrics.extend(str(lyr).split("<ENDLINE>"))
        #breakpoint()
        nLyrics = len(current_lyrics)
        bound1 = int(nLyrics*0.4)
        bound2 = int(nLyrics*0.9)
        candidates = current_lyrics[:bound1]
        feature = current_lyrics[bound1:bound2]
        history = current_lyrics[bound2:]
        history = " ".join(history)
        utterances = {"candidates": candidates, "history": [history]}
        output.append({"feature": feature, "utterances": utterances})
        
    return output


def construct_dataset():
    # read in lyrics as dataframe
    lyrics = pandas.read_csv(LYRICS_DATA)

    # downsample the data (need to do this because of errors with pretrained model input layer size)
    # TODO fix this, figure out why its too large
    msk1 = np.random.rand(len(lyrics)) < 0.1
    msk2 = np.random.rand(len(lyrics)) > 0.98
    train_lyrics = lyrics[msk1]
    validate_lyrics = lyrics[msk2]
    train_list = parse_dataframe(train_lyrics)
    validate_list = parse_dataframe(validate_lyrics)
    return {"train": train_list, "valid": validate_list}


def get_dataset(tokenizer, dataset_cache):
    if dataset_cache and os.path.isfile(dataset_cache) and False:
        dataset = torch.load(dataset_cache)
    else:
        dataset = construct_dataset()

        def tokenize(simplex):
            if isinstance(simplex, str):
                return tokenizer.convert_tokens_to_ids(tokenizer.tokenize(simplex))
            if isinstance(simplex, dict):
                return dict((n, tokenize(o)) for n, o in simplex.items())
            return list(tokenize(o) for o in simplex)
        dataset = tokenize(dataset)
        torch.save(dataset, dataset_cache)
    return dataset
