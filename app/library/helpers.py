import os.path
import markdown
import json


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def load_errors_lookup(root):
    """
    Load the errors that are matched to clusters
    """
    filename = os.path.join(
        root, "data", "clusters", "dbstream", "cluster-assignments.json"
    )
    if not os.path.exists(filename):
        sys.exit(f"{filename} does not exist, required for server functionality.")
    errors = read_json(filename)
    return sorted(errors.items(), key=lambda x: x[0])


def load_errors_specs_lookup(root):
    """
    load specs that are matched to the same clusters
    """
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
