"""Scan files (and the members of zip files) for personal details or key-like strings.

Used by tools/git_gate.ps1 before every commit. Prints the file name, the name of the
pattern and a count only - never the matched text. Exit code 0 = nothing found, 1 = found.
"""
import re
import sys
import zipfile

ALLOWED_EMAIL_SUFFIXES = (b"noreply.github.com", b"noreply@anthropic.com")

PATTERNS = {
    "home_directory_path": re.compile(rb"[Uu]sers[\\/]+[A-Za-z0-9_.-]+"),
    "email": re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "github_token": re.compile(rb"gh[opusr]_[A-Za-z0-9]{20,}"),
    "private_key_block": re.compile(rb"BEGIN [A-Z ]*PRIVATE KEY"),
    "credential_assignment": re.compile(
        rb"(api[_-]?key|api[_-]?secret|password|passwd)\s*[=:]\s*['\"][^'\"]{6,}", re.I
    ),
}


def scan(name, data, out):
    for label, pat in PATTERNS.items():
        hits = pat.findall(data)
        if label == "email":
            hits = [h for h in hits if not h.endswith(ALLOWED_EMAIL_SUFFIXES)]
        if hits:
            out.append((name, label, len(hits)))


def main(argv):
    out = []
    scanned = 0
    for path in argv[1:]:
        if path.lower().endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                for n in z.namelist():
                    if n.endswith("/"):
                        continue
                    scan("zip:" + path + ":" + n, z.read(n), out)
                    scanned += 1
        else:
            with open(path, "rb") as fh:
                scan(path, fh.read(), out)
            scanned += 1
    if not out:
        print("private-detail scan: NO MATCHES in %d files" % scanned)
        return 0
    for name, label, count in out:
        print("%-24s x%-4d %s" % (label, count, name))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
