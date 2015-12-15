from posts import makeDailyPost, makeOtherPost
import sys

if len(sys.argv) != 2:
    raise Exception("Incorrect number of argument received")
else:
    if sys.argv[1] == '--hourly':
        # Ensure that we haven't posted today's post yet.
        makeDailyPost()
    elif sys.argv[1] == '--daily':
        makeOtherPost()
    else:
        raise Exception("Unknown argument received")
