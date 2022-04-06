from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from glob import glob
import json
import re
import os

# Derive stop words and stemmer once
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


def write_json(content, filename):
    with open(filename, "w") as fd:
        fd.write(json.dumps(content, indent=4))


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def read_errors(datadir):
    errors = []
    for filename in glob(os.path.join(datadir, "errors*.json")):
        errors += read_json(filename)
    print("Found %s spack-monitor errors!" % len(errors))

    # Figure out last id
    ids = [e["id"] for e in errors]
    ids.sort()
    newid = ids[-1] + 1

    # Add in dinos errors
    dinodir = os.path.join(datadir, "dinos")
    if os.path.exists(dinodir):
        for filename in glob(os.path.join(dinodir, "*error.json")):
            entries = read_json(filename)
            for entry in entries:
                entry["id"] = newid
                entry["label"] = "dinos-error"
                newid += 1
                errors.append(entry)

    print("Found a total of %s errors" % len(errors))

    # Replace source file None with empty
    for error in errors:
        if error["source_file"] in [[None], (None,)]:
            error["source_file"] = ""
    return errors


def process_text(text):
    """
    Process text, including:

    1. Lowercase
    2. Remove numbers and punctuation
    3. Strip whitespace
    4. Tokenize and stop word removal
    5. Stemming
    """
    # Make lowercase
    text = text.lower()

    # Remove numbers and punctuation (but leave path separator for now)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s\/]", "", text)

    # Strip whitespace
    text = text.strip()

    # tokenize and stop word removal
    words = []
    for token in word_tokenize(text):
        if token in stop_words:
            continue
        if os.sep in token:
            token = os.path.basename(token)
        words.append(token)

    # Don't do stemming here - the error messages are usually hard coded / consistent
    # words = [stemmer.stem(t) for t in tokens]
    return words
