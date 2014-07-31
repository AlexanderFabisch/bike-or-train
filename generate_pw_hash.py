import sys
from werkzeug.security import generate_password_hash


if __name__ == "__main__":
    pw = sys.argv[1]
    pw_hash = generate_password_hash(pw)
    open("pw.hash", "w").write(pw_hash)

