with open("data/incoming/DSCI.txt", "rb") as f:
    raw = f.read(100)
    print(repr(raw))