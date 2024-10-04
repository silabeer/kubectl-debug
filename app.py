from flask import Flask
from redis import Redis, RedisError
import os
import socket
import pickledb

# Connect to Redis
redis = Redis(host="redis", port=6379,
              db=0, socket_connect_timeout=2, socket_timeout=2)
# ...or a local (file-based) Pickle DB
pickle_db = pickledb.load('/data/pysimple.db', True)

COUNTER_FIELD = 'counter'

app = Flask(__name__)


@app.route("/")
def hello():
    # Try to use Redis
    # and then fall-back to a pickle database...
    try:
        visits = redis.incr(COUNTER_FIELD)
    except Exception as r_ex:
        print('WARNING: redis.incr(%s) returned %s' %
              (COUNTER_FIELD, r_ex))
        try:
            visits = pickle_db.get(COUNTER_FIELD)
        except Exception as p_ex:
            print('WARNING: pickle_db.get(%s) returned %s' %
                  (COUNTER_FIELD, p_ex))
        # Initialise visits if we need to
        # and then increment
        if not visits:
            visits = 0
        visits += 1
        try:
            pickle_db.set(COUNTER_FIELD, visits)
        except Exception as p_ex:
            print('WARNING: pickle_db.set(%s) returned %s' %
                  (COUNTER_FIELD, p_ex))

    # visits should be set to something here,
    # either via a Redis increment or via a pickle-db instance,
    # or just a memory resident value.

    html = "<h3>Hello {name}!</h3>\n" \
           "Hostname: {hostname} <br/>\n" \
           "Num visits: {visits}\n"
    return html.format(name=os.getenv("NAME", "world"),
                       hostname=socket.gethostname(), visits=visits)


if __name__ == "__main__":

    # If I enable `debug=True` I get
    # `KeyError: 'getpwuid(): uid not found: 1000060000'` errors
    # from OpenShift.
    app.run(host='0.0.0.0', port=8080)