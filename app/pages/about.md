# About

In this small project we will:

1. start with current errors from the spack monitor API
2. generate DBSTREAM clusters using river to describe them
3. save output of cluster assignments to file
4. generate another classification model to associate with features

## Classification Plan

We are planning the following workflow:

 - start with errors from spack
 - cluster with dbstream and save assignments
 - extract features for specs (both success and failed)
 - for an error (associated with a failed spec) find most similar specs that were successful
 - do a diff to see if we can give actionable advice

Will we be successful? Who knows! It will be fun to test it out.
