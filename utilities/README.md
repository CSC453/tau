`visitor.py` is created from `visitor.toml` using the following command in the top-level directory:

```bash
$ python3 -m tau.utilities.mktemplate.py --spec tau/utilities/visitor.toml --output /tmp/visitor.py
```

Followed by
    
```bash
$ cp /tmp/visitor.py tau/utilities/visitor.py
```

The reason for this two-step process is because `visitor.py` is needed to create itself.