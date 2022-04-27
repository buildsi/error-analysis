import os
import sys
import json
import math
import operator
from helpers import read_yaml, write_json
import pandas as pd
from specutils import get_features_from_spec, get_cluster_data


def get_spec(uid):
    spec_file = os.path.join(
        os.getcwd(), "data", "spec_files", "errors", "%s.yaml" % uid
    )
    if not os.path.exists(spec_file):
        sys.exit("%s does not exist." % spec_file)
    return read_yaml(spec_file)


def tfidf(freq_table, cluster_id, num_clusters):
    tfid = dict()
    for index, row in freq_table.iterrows():
        inv_freq = math.log(num_clusters / (1 + row.ne(0).sum()))
        tfid[index] = row[cluster_id] * inv_freq

    return dict(sorted(tfid.items(), key=operator.itemgetter(1), reverse=True))


def get_feature_count(cluster_data):
    num_clusters = max(cluster_data.values())
    feat_count = pd.DataFrame(columns=list(range(0, num_clusters + 1)))
    lst = [0] * num_clusters

    for id, cluster in cluster_data.items():
        spec = get_spec(id)
        spec_feat_list = get_features_from_spec(spec)
        print(id, cluster)
        for feat in spec_feat_list:
            if feat in feat_count.index:
                feat_count.loc[feat, cluster] += 1
            else:
                xs = pd.Series(lst)
                xs[cluster] = 1
                xs.name = feat
                feat_count = feat_count.append(xs)

    return feat_count


def main():

    cluster_data = get_cluster_data()
    num_clusters = max(cluster_data.values())
    unique_feats = set()
    feat_count = get_feature_count(cluster_data)

    tfids = []
    datadir = "data"
    save_prefix = "tfidf"
    for cluster_id in range(num_clusters):
        val = tfidf(feat_count, cluster_id, num_clusters)
        tfids.append(val)

        cluster_dir = os.path.join(datadir, "feature-ranking", save_prefix)
        if not os.path.exists(cluster_dir):
            os.makedirs(cluster_dir)

        cluster_meta = os.path.join(cluster_dir, "cluster-feats-%s.json" % cluster_id)
        write_json(val, cluster_meta)


if __name__ == "__main__":
    main()
