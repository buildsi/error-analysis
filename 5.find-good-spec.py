import os
import sys
import pandas as pd
import numpy as np
from helpers import read_json
from specutils import get_cluster_data

good_specs = pd.DataFrame()


def get_features_from_file(feat_file):
    """
    Given a spec feature file return the features.
    """
    feats = read_json(feat_file)
    feats_dict = dict.fromkeys(feats, 1)
    return feats_dict


def get_features(spec_dir, uid):
    """
    Given a spec feature directory and an id read from the spec feature file
    and return the featues.
    """
    feature_file = os.path.join(spec_dir, "%s.json" % uid)
    if not os.path.exists(feature_file):
        sys.exit("%s does not exist." % feature_file)

    return get_features_from_file(feature_file)


def get_feature_weights(cluster_id):
    """
    Given a cluster id, get the feature weights
    """
    cluster_dir = os.path.join(os.getcwd(), "data", "feature-ranking", "tfidf")
    cluster_meta = os.path.join(cluster_dir, "cluster-feats-%s.json" % cluster_id)

    if not os.path.exists(cluster_meta):
        sys.exit("%s file does not exist.", cluster_meta)

    return read_json(cluster_meta)


def get_all_good_specs():
    """
    Get features for all the good specs.
    """

    good_spec_data = []

    good_spec_dir = os.path.join(os.getcwd(), "data", "feature-specs", "working")
    for root, subdirs, files in os.walk(good_spec_dir):
        for filename in files:
            spec_file = os.path.join(good_spec_dir, root, filename)
            spec_feats = get_features_from_file(spec_file)
            spec_hash = os.path.splitext(filename)[0]
            spec_feats["uid"] = spec_hash
            # print(spec_hash)
            good_spec_data.append(spec_feats)

    return good_spec_data


def find_nearest_good_spec(uid, cluster):
    """
    Given a spec uid and the corresponding cluster, find the closest good spec.
    """
    err_spec_dir = os.path.join(os.getcwd(), "data", "feature-specs", "errors")

    # For the given error spec do the following:
    # 1. Get the features for the spec.
    # 2. Get the tfidf weights for the corresponding cluster.
    # 3. Use tfidf weights to scale the features.
    # 4. Find the closest good spec.
    feat = get_features(err_spec_dir, uid)
    feat_weights = get_feature_weights(cluster)

    feat_df = pd.DataFrame(feat, index=[0])
    feat_weight_df = pd.DataFrame(feat_weights, index=[0])

    # Get all the good specs
    global good_specs
    if good_specs.empty:
        good_spec_data = get_all_good_specs()
        good_specs = pd.DataFrame.from_dict(good_spec_data).fillna(0).set_index("uid")

    # Populate missing features
    all_cols = set(good_specs.columns)
    all_cols.update(list(feat_weight_df.columns))

    good_specs = good_specs.reindex(all_cols, axis="columns", fill_value=0)
    feat_weight_df = feat_weight_df.reindex(all_cols, axis="columns", fill_value=0)
    feat_df = feat_df.reindex(all_cols, axis="columns", fill_value=0)

    # Normalize the weights
    feat_normalized = np.nan_to_num(
        feat_weight_df.to_numpy() / feat_weight_df.to_numpy().sum(axis=1)
    )
    # Weight the features of error spec
    feat_weighted = feat_df.to_numpy() * feat_normalized

    # Calculate distance score
    # The following can be replaced with KNN.
    good_spec_score = np.matmul(good_specs.to_numpy(), np.transpose(feat_weighted))
    # Return the uid for the closest good spec and the score
    return good_specs.iloc[np.argmax(good_spec_score)].name, np.max(good_spec_score)


def main():

    cluster_data = get_cluster_data()

    # Get the nearest good spec for each spec that is in the cluster database.
    for id, cluster in cluster_data.items():
        good_spec, score = find_nearest_good_spec(id, cluster)
        print(id, " cluster #", cluster, " closest good spec: ", good_spec, score)


if __name__ == "__main__":
    main()
