#!/usr/bin/env python


from riverapi.main import Client
from river import cluster, feature_extraction, neighbors
from scipy.spatial.distance import pdist, squareform
from sklearn import manifold
from creme import feature_extraction as creme_features

import pandas
import argparse
import sys
import os
import pickle
import json

sys.path.insert(0, os.getcwd())
from helpers import process_text, write_json, read_errors, read_yaml

here = os.path.dirname(os.path.abspath(__file__))

# Note that knn.py here isn't used, we use this common module
# so that we can later import into spack monitor and install the same class
from online_ml_custom.creme.knn import KNeighbors


def get_parser():
    parser = argparse.ArgumentParser(
        description="Spack Monitor Online ML",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--data_dir",
        help="Directory with data",
        default=os.path.join(os.getcwd(), "data"),
    )
    parser.add_argument("--iter", help="Iterations to run", default=5, type=int)

    return parser


class ModelBuilder:
    def __init__(self, errors, host="http://127.0.0.1:8000", prefix=None, datadir=None):
        self.errors = errors
        self.datadir = datadir

    def iter_sentences(self):
        """
        Yield sentences (parsed) to learn from.
        """
        for i, entry in enumerate(self.errors):
            print("%s of %s" % (i, len(self.errors)), end="\r")

            # Pre, text, and post
            raw = entry.get("text")
            if not raw:
                continue

            # Split based on error
            if "error:" not in raw:
                continue

            text = raw.split("error:", 1)[-1]
            tokens = process_text(text)
            sentence = " ".join(tokens)

            # Skip single words!
            if not tokens or not sentence.strip() or len(tokens) == 1:
                continue
            yield sentence, entry["hash"]

    def load_spec(self, uid):
        """
        Load the spec from data/spec_file
        """
        spec_file = os.path.join(here, "data", "spec_files", "%s.yaml" % uid)
        if not os.path.exists(spec_file):
            sys.exit("%s does not exist!" % spec_file)
        return read_yaml(spec_file)

    def dbstream(
        self, model_name="dbstream-errors", save_prefix="dbstream", iterations=5
    ):
        """
        Build the dbstream model with a particular name.
        https://riverml.xyz/latest/api/cluster/DBSTREAM
        """
        model = feature_extraction.BagOfWords() | cluster.DBSTREAM(
            clustering_threshold=1.5,
            fading_factor=0.05,
            cleanup_interval=4,
            intersection_factor=0.5,
            minimum_weight=1,
        )

        # Make sure the model sees each one N=iter times
        for _ in range(iterations):
            for sentence, _ in self.iter_sentences():
                model.learn_one(x=sentence)

        # Save clusters to file under data/clusters/<prefix>
        self.generate_clusters_json(model, save_prefix)
        self.save_model(model, model_name)
        return model

    def generate_clusters_json(self, model, save_prefix):
        """
        Generate json cluster output for visual inspetion
        """
        # At this point, let's get a prediction for each
        # We can just group them based on the cluster
        clusters = {}
        assigned = {}
        for sentence, uid in self.iter_sentences():

            # Harshitha - here is an example of loading the spec
            spec = self.load_spec(uid)
            # print(json.dumps(spec, indent=4))
            res = model.predict_one(x=sentence)
            if res not in clusters:
                clusters[res] = []
            clusters[res].append(sentence)
            assigned[uid] = res

        # Make model output directory
        cluster_dir = os.path.join(self.datadir, "clusters", save_prefix)
        if not os.path.exists(cluster_dir):
            os.makedirs(cluster_dir)

        for cluster_id, entries in clusters.items():
            if not entries:
                continue
            cluster_meta = os.path.join(
                cluster_dir, "cluster-tokens-%s.json" % cluster_id
            )
            write_json(entries, cluster_meta)

        save_to = os.path.join(cluster_dir, "error-assignments.json")
        write_json(assigned, save_to)

    def save_model(self, model, model_name):
        """
        Save a pickled model (and return it)
        """
        # Download the model and load to get centroids
        pickle.dump(model, open(f"{model_name}.pkl", "wb"))

    def load_model(self, pkl):
        """
        Load a model from pickle
        """
        with open(pkl, "rb") as fd:
            model = pickle.load(fd)
        return model


def generate_embeddings(centers, name):
    df = pandas.DataFrame(centers)

    # 200 rows (centers) and N columns (words)
    df = df.transpose()
    df = df.fillna(0)

    # Create a distance matrix
    distance = pandas.DataFrame(
        squareform(pdist(df)), index=list(df.index), columns=list(df.index)
    )

    # Make the tsne (output embeddings go into docs for visual)
    fit = manifold.TSNE(n_components=2)
    embedding = fit.fit_transform(distance)
    emb = pandas.DataFrame(embedding, index=distance.index, columns=["x", "y"])
    emb.index.name = "name"
    emb.to_csv(os.path.join("docs", "%s-software-embeddings.csv" % name))


def main():

    parser = get_parser()
    args, extra = parser.parse_known_args()

    # Make sure output directory exists
    datadir = os.path.abspath(args.data_dir)
    if not os.path.exists(datadir):
        sys.exit("%s does not exist!" % datadir)

    # Build model with errors
    errors = read_errors(datadir)

    if not os.path.exists("docs"):
        os.makedirs("docs")

    builder = ModelBuilder(datadir=datadir, errors=errors)
    model = builder.dbstream(model_name="spack-dbstream-errors", iterations=args.iter)


if __name__ == "__main__":
    main()
