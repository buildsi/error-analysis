import os
from helpers import read_yaml
from specutils import get_features_from_spec


def main():
  spec_dir =  os.path.join(os.getcwd(), "data", "spec_files", "working")
  for root,subdirs,files in os.walk(spec_dir):
    for file in files:
      spec_file = os.path.join(spec_dir, root, file)
      spec = read_yaml(spec_file)
      spec_feat = get_features_from_spec(spec)

if __name__ == "__main__":
    main()
