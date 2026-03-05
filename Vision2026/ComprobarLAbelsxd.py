import os, glob

train_imgs = glob.glob(r"C:\git\Arabots-Classes2\Vision2026\Test\images\train\*.jpg")
val_imgs   = glob.glob(r"C:\git\Arabots-Classes2\Vision2026\Test\images\val\*.jpg")

train_lbls = glob.glob(r"C:\git\Arabots-Classes2\Vision2026\Test\labels\train\*.txt")
val_lbls   = glob.glob(r"C:\git\Arabots-Classes2\Vision2026\Test\labels\val\*.txt")

print("Train imgs:", len(train_imgs), " Train labels:", len(train_lbls))
print("Val imgs:", len(val_imgs), " Val labels:", len(val_lbls))

# cuenta cuántos labels NO están vacíos
def count_nonempty(files):
    c = 0
    for f in files:
        if os.path.getsize(f) > 0:
            c += 1
    return c

print("Train labels NO vacíos:", count_nonempty(train_lbls))
print("Val labels NO vacíos:", count_nonempty(val_lbls))
