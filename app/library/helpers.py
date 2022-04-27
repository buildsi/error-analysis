import os.path
import markdown
import json
import sys
import pandas as pd


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def load_errors_lookup(root):
    """
    Load the errors that are matched to clusters
    """
    print("Loading errors lookup...")
    filename = os.path.join(
        root, "data", "clusters", "dbstream", "cluster-assignments.json"
    )
    if not os.path.exists(filename):
        sys.exit(f"{filename} does not exist, required for server functionality.")
    errors = read_json(filename)
    return sorted(errors.items(), key=lambda x: x[0])


def get_features_from_file(feat_file):
    """
    Given a spec feature file return the features.
    """
    feats = read_json(feat_file)
    feats_dict = dict.fromkeys(feats, 1)
    return feats_dict


def load_good_specs(root):
    """
    Get a pandas data frame for features for all the good specs.
    """
    print("Loading good spec features (this may take a few seconds)...")
    good_spec_data = []
    good_spec_dir = os.path.join(root, "data", "feature-specs", "working")
    for root, subdirs, files in os.walk(good_spec_dir):
        for filename in files:
            spec_file = os.path.join(good_spec_dir, root, filename)
            spec_feats = get_features_from_file(spec_file)
            spec_hash = os.path.splitext(filename)[0]
            spec_feats["uid"] = spec_hash
            good_spec_data.append(spec_feats)
    df = pd.DataFrame.from_dict(good_spec_data).fillna(0).set_index("uid")
    print("Size of good spec features data frame is %s %s" % df.shape)
    return df


def load_errors_specs_lookup(root):
    """
    load specs that are matched to the same clusters
    """
    print("Loading errors specs lookup...")
    filename = os.path.join(
        root, "data", "clusters", "dbstream", "error-assignments.json"
    )
    if not os.path.exists(filename):
        sys.exit(f"{filename} does not exist, required for server functionality.")
    return read_json(filename)


def openfile(filename):
    filepath = os.path.join("app/pages/", filename)
    with open(filepath, "r", encoding="utf-8") as input_file:
        text = input_file.read()

    html = markdown.markdown(text)
    data = {"text": html}
    return data
