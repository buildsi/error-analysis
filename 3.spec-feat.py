import os
from helpers import read_yaml, write_json
from specutils import get_features_from_spec


def generate_features(spec_dir, spectype):
    """
    Given a spec type (working or errors) that maps to the directory,
    generate spec-level features. Each is a set.
    """
    feature_dir = os.path.join(os.getcwd(), "data", "feature-specs", spectype)
    if not os.path.exists(feature_dir):
        os.makedirs(feature_dir)
    for root, subdirs, files in os.walk(spec_dir):
        for filename in files:
            spec_file = os.path.join(spec_dir, root, filename)
            spec = read_yaml(spec_file)
            spec_feat = get_features_from_spec(spec)
            outfile = os.path.join(feature_dir, filename.replace(".yaml", ".json"))
            write_json(list(spec_feat), outfile)


def main():

    # Generate features for both working and errors
    for spectype in ["working", "errors"]:
        spec_dir = os.path.join(os.getcwd(), "data", "spec_files", "working")
        generate_features(spec_dir, spectype)


if __name__ == "__main__":
    main()
