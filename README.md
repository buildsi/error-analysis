# Error Analysis

In this small project we will:

1. start with current errors from the spack monitor API
2. generate DBSTREAM clusters using river to describe them
3. save output of cluster assignments to file
4. generate another classification model to associate with features

Right now we have a basic set of errors, and we will need to get specs (the features) in
this repo too. @vsoch will wait to see a spec from Dinos set and then ensure the spack
monitor ones are exported to be the same.

## Usage

```bash
$ python -m venv env
$ source env/bin/activate
$ conda install river
$ pip install -r requirements.txt
```

**Important** @vsoch fixed some bugs with dbstream so you'll need to install river from GitHub

```bash
$ git clone https://github.com/online-ml/river
$ cd river
$ pip install -e .
```

For now we are using already downloaded data from spack monitor instances, provided
in the repository (minus the specs so far!)

### Online ML

Note that pre-processing of dinos (raw) data was done via [1.data.py](1.data.py)
and you don't need to run it again! It basically flattened the original errors data and added the hash
at the same level, and created an errors lookup for the web application.

The script [2.online-ml.py](2.online-ml.py) will generate the clusters in [data/clusters](data/clusters).
The default number of iterations is 5 but you can specify a custom value:

```bash
$ python 2.online-ml.py --iter 5
```

## Classification Plan

**Harshitha please add notes here!** It would be good to know where each data is stored.

We are planning the following workflow:

 - start with errors (in [data/errors*.json](data/) and [data/dinos](data/dinos))
 - cluster with dbstream (clusters in [data/clusters/dbstream/](data/clusters/dbstream/))
 - extract features for specs (both success and failed) (we need specs added to the repository)
 - for an error (associated with a failed spec) find most similar specs that were successful
 - do a diff to see if we can give actionable advice

```
error -> cluster -> failed specs from cluster -> features for failed specs -> find similar working specs -> spack diff
```

## Web Interface

We are working on a basic web interface here to let you explore the online ML results! I don't have the specs etc. from
Harshitha yet, but I started a basic [app](app) preparing for that.

```bash
$ pip install -r app-requirements.txt
```

and then to run the app:

```bash
$ uvicorn app.main:app --host=0.0.0.0 --port=5000
```

You can also use the Makefile:

```bash
$ make
```

## License

Spack is distributed under the terms of both the MIT license and the
Apache License (Version 2.0). Users may choose either license, at their
option.

All new contributions must be made under both the MIT and Apache-2.0
licenses.

See [LICENSE-MIT](https://github.com/spack/spack/blob/develop/LICENSE-MIT),
[LICENSE-APACHE](https://github.com/spack/spack/blob/develop/LICENSE-APACHE),
[COPYRIGHT](https://github.com/spack/spack/blob/develop/COPYRIGHT), and
[NOTICE](https://github.com/spack/spack/blob/develop/NOTICE) for details.

SPDX-License-Identifier: (Apache-2.0 OR MIT)

LLNL-CODE-811652
