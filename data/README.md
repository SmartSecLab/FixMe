After running the code in the parent directory of the repository using the command:

```
python3 -m source.collect
```

You will get the CVElistV5 folder which mirrors the repository of CVE records. Furthermore, output database file named `FixMe.db` will be generated as specified in the `config.yaml` configuration file.
The database file stores the information of different granularity levels open-source project repositories which can be utilized for different software security applications, i.e., automated patch prediction, automated program repair, commit classification, vulnerability prediction, etc.
