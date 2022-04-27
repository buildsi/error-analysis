import os
import numpy as np
import pandas as pd
import yaml
import json


def load_spec(root, digest, spectype="errors"):
    """
    Given a spec id, load from the data directory
    """
    spec_file = os.path.join(root, "data", "spec_files", spectype, "%s.yaml" % digest)
    if os.path.exists(spec_file):
        with open(spec_file, "r") as fd:
            content = yaml.safe_load(fd.read())
        return content


def load_features(root, cluster_id):
    """
    Given a cluster id, load features for it
    """
    features_file = os.path.join(
        root, "data", "feature-ranking", "tfidf", "cluster-feats-%s.json" % cluster_id
    )
    if os.path.exists(features_file):
        with open(features_file, "r") as fd:
            content = json.loads(fd.read())
        return content


def load_spec_features(root, digest, spectype="errors"):
    """
    Given a spec hash (and type), load features for it
    """
    features_file = os.path.join(
        root, "data", "feature-specs", spectype, "%s.json" % digest
    )
    if os.path.exists(features_file):
        with open(features_file, "r") as fd:
            content = json.loads(fd.read())
        return content


def find_single_nearest_good_spec(root, error_spec_features, cluster_id, good_specs):
    """
    Given a spec uid and the corresponding cluster, find the closest good spec.
    We load the single spec features and normalize according to the cluster.
    """
    # For the given error spec do the following:
    # 1. Get the features for the spec.
    # 2. Get the tfidf weights for the corresponding cluster.
    # 3. Use tfidf weights to scale the features.
    # 4. Find the closest good spec.
    feat_weights = load_features(root, cluster_id)

    feat_df = pd.DataFrame(error_spec_features, index=[0])
    feat_weight_df = pd.DataFrame(feat_weights, index=[0])

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
    # The following can be replaced with KNN for a more production instance (if this works)
    good_spec_score = np.matmul(good_specs.to_numpy(), np.transpose(feat_weighted))
    good_spec_features = good_specs.iloc[np.argmax(good_spec_score)].to_dict()
    good_spec_uid = good_specs.iloc[np.argmax(good_spec_score)].name

    # Return the uid for the closest good spec and the score
    return good_spec_features, good_spec_uid, np.max(good_spec_score)


def find_cluster_nearest_good_spec(feat_weights, good_specs):
    """
    Given a cluster id, find the closest good spec.
    """
    # For the given error cluster do the following:
    # 1. Get tfidf features for the cluster
    # 2. Find the closest good spec.
    # Are these normalized already?
    feat_weight_df = pd.DataFrame(feat_weights, index=[0])

    # Populate missing features
    all_cols = set(good_specs.columns)
    all_cols.update(list(feat_weight_df.columns))

    good_specs = good_specs.reindex(all_cols, axis="columns", fill_value=0)
    feat_weight_df = feat_weight_df.reindex(all_cols, axis="columns", fill_value=0)

    # The weights are already normalized?
    feat_weights_vector = np.nan_to_num(feat_weight_df.to_numpy())

    # Calculate distance score
    # The following can be replaced with KNN.
    good_spec_score = np.matmul(
        good_specs.to_numpy(), np.transpose(feat_weights_vector)
    )

    # These are the good spec features we can use to diff
    good_spec_features = good_specs.iloc[np.argmax(good_spec_score)].to_dict()
    good_spec_uid = good_specs.iloc[np.argmax(good_spec_score)].name

    # Return the uid for the closest good spec and the score
    return good_spec_features, good_spec_uid, np.max(good_spec_score)
