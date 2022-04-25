#!/usr/bin/env python

# Scripts to process specs into format we can associate with errors

# each file in dbs (pickle) is named by the package

import os
import sys
import pickle

sys.path.insert(0, os.getcwd())
from helpers import process_text, write_json, read_errors, read_json

here = os.path.abspath(os.path.dirname(__file__))
dbs_dir = os.path.join(here, "data", "raw")
out_dir = os.path.join(here, "data", "dinos")
dbs = os.listdir(dbs_dir)

# keep track of spec files we are missing
missing = set()

# This will basically squash dinos error files into a single flat list of dict
for db_file in dbs:
    outfile = os.path.join(out_dir, db_file)
    err = read_json(os.path.join(dbs_dir, db_file))
    # Create a final output folder for the package
    errors = []
    for entry in err:
        data = entry["snippet"]
        data["hash"] = entry["hash"]
        errors.append(data)

        # Ensure that the spec exists
        spec_file = os.path.join(here, "data", "spec_files", "%s.yaml" % data["hash"])
        if not os.path.exists(spec_file):
            missing.add(spec_file)

    write_json(errors, outfile)

# Create a lookup of errors to clusters
clusters_dir = os.path.join(here, "data", "clusters", "dbstream")
clusters = os.listdir(clusters_dir)
error_lookup = {}

for cluster_file in clusters:
    cluster_data = read_json(os.path.join(clusters_dir, cluster_file))

    # Skip files that are error-assignments
    if "assignments" in cluster_file:
        continue
    cluster_id = int(cluster_file.replace(".json", "").split("-")[-1])
    for e in cluster_data:
        if e not in error_lookup:
            error_lookup[e] = set()
        error_lookup[e].add(cluster_id)

# Now ensure we have lists to save to file
for e in error_lookup:
    error_lookup[e] = list(error_lookup[e])
    assert len(error_lookup[e]) == 1
    error_lookup[e] = error_lookup[e][0]
outfile = os.path.join(clusters_dir, "cluster-assignments.json")
write_json(error_lookup, outfile)
