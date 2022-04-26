import os
from helpers import read_yaml


def get_features_from_spec(spec):
    spec_feat_list = set()
    nodes = spec['spec']['nodes']
    for node in nodes:

        name = node['name']
        version = node['version']
        arch = node['arch']['target']['name']
        compiler = node['compiler']['name']
        compiler_version = node['compiler']['version']
        compiler_cflags = node['parameters']['cflags']
        compiler_cxxflags = node['parameters']['cxxflags']
        compiler_ldflags = node['parameters']['ldflags']
        compiler_ldlibs = node['parameters']['ldlibs']

        node_feat = [name+'#'+version, arch, compiler, compiler+'@'+compiler_version]
        if 'cuda' in node['parameters'].keys():
            if node['parameters']['cuda']:
                node_feat.append('cuda_on')

        if len(compiler_cflags) != 0:
            print(compiler_cflags)
            node_feat.append(compiler_cflags)
        if len(compiler_cxxflags) != 0:
            node_feat.append(compiler_cxxflags)
        if len(compiler_ldflags) != 0:
            node_feat.append(compiler_ldflags)
        if len(compiler_ldlibs) != 0:
            node_feat.append(compiler_ldlibs)

        spec_feat_list.update(node_feat)
    return spec_feat_list

 
def main():
  spec_dir =  os.path.join(os.getcwd(), "data", "spec_files", "working")
  for root,subdirs,files in os.walk(spec_dir):
    for file in files:
      spec_file = os.path.join(spec_dir, root, file)
      spec = read_yaml(spec_file)
      spec_feat = get_features_from_spec(spec)

if __name__ == "__main__":
    main()
