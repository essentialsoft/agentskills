import argparse
import json
import traceback
import mgclient

parser = argparse.ArgumentParser()

parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", default=7687)
parser.add_argument("--username", default="user")
parser.add_argument("--password", default="password")
parser.add_argument("--query", required=True)

parser.add_argument("--skip", type=int, default=0)
parser.add_argument("--limit", type=int, default=5)

args = parser.parse_args()

try:
    conn = mgclient.connect(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password
    )

    cursor = conn.cursor()

    params = {}
    if "$skip" in args.query or "$SKIP" in args.query:
        params["skip" if "$skip" in args.query else "SKIP"] = args.skip
    if "$limit" in args.query or "$LIMIT" in args.query:
        params["limit" if "$limit" in args.query else "LIMIT"] = args.limit

    if params:
        cursor.execute(args.query, params)
    else:
        cursor.execute(args.query)

    results = cursor.fetchall()

    print(
        json.dumps(
            {
                "success": True,
                "row_count": len(results),
                "results": results
            },
            default=str
        )
    )

except Exception as e:
    print(
        json.dumps(
            {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )
    )