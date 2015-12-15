from posts import tryPost
import sys

valid_arguments = ['topical','discussion']


if len(sys.argv) != 2:
    raise Exception("Incorrect number of argument received")
else:
    if any(arg == sys.argv[1] for arg in valid_arguments):
        tryPost(sys.argv[1])
    else:
        raise Exception("Unknown argument received")
