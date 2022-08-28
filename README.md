# Error Analysis

In this small project we will:

1. start with current errors from the spack monitor API
2. generate DBSTREAM clusters using river to describe them
3. save output of cluster assignments to file
4. generate another classification model to associate with features

Right now we have a basic set of errors, and we will need to get specs (the features) in
this repo too. @vsoch will wait to see a spec from Dinos set and then ensure the spack
monitor ones are exported to be the same.

## Classification Plan

We are planning the following workflow:

 - start with errors (in [data/errors*.json](data/) and [data/dinos](data/dinos))
 - cluster with dbstream (clusters in [data/clusters/dbstream/](data/clusters/dbstream/))
 - extract features for specs (both success and failed)
 - for an error cluster (associated with one or more failed specs and summary of features) find most similar specs that were successful (based on features)
 - see if the diff makes sense and we can give actionable advice.

```
error -> cluster -> failed specs from cluster -> features for failed specs -> find similar working specs -> spack diff
```


## Usage

```bash
$ python -m venv env
$ source env/bin/activate
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

### Interfaces

Here are some quick shots of the interfaces, first home:

![img/home.png](img/home.png)

And selecting a cluster:

![img/cluster.png](img/cluster.png)

Expanding a spec:

![img/spec.png](img/spec.png)

Comparing features:

![img/features.png](img/features.png)

And diffing two specs:

![img/diff.png](img/diff.png)

Red/green shows changes (deletions and additions), and blue highlights are features.

### Data Preprocessing

Note that pre-processing of dinos (raw) data was done via [1.data.py](1.data.py)

**Important** there are two specs in the 'errors database' that had error messages but actually were successful installs by
spack. We have filtered them out in [1.data.py](1.data.py). These errors would not have been parsed by spack monitor.
After you run this, you should have data/errors*.json files with all errors. We will be using these
files for the model building, discussed next.


### Online ML

The script [2.online-ml.py](2.online-ml.py) will generate the clusters in [data/clusters](data/clusters).
The default number of iterations is 5 but you can specify a custom value:

```bash
$ python 2.online-ml.py --iter 5
```

Then generate features for the working clusters:

```bash
$ python 3.spec-feat.py
```

And the error clusters:


```bash
$ python 4.tfidf-feat.py
```

Find the closest good spec for error specs:


```bash
$ python 5.find-good-spec.py
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

Note that since we need to load a lot of data to the app on startup, it might
take a few seconds (you should open your browser to [http://127.0.0.1:5000](http://127.0.0.1:5000)
to trigger the first load). After this load most pages will be realtively quick because
we have the data loaded, with the exception of showing an entire page of error specs,
the reason because we have to load those on demand.

## TODO

- side by side full spec with features able to highlight
- add error context to top of spec diff page

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
