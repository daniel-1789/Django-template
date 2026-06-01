#!/usr/bin/env bash
# Populate the database with sample manufacturers and items by POSTing to the
# running API. Manufacturers are created first so their IDs can be used as the
# items' foreign keys.
#
# Usage:
#   ./seed.sh                          # seeds http://127.0.0.1:5000 (Flask's default)
#   BASE_URL=http://127.0.0.1:8099 ./seed.sh
#
# The API must already be running (flask --app app run) and migrated
# (alembic upgrade head). This hits the HTTP endpoints, so it works the same
# whether the backend is SQLite or MySQL.

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:5000}"

post_json() {  # post_json <url> <json-body>
  curl -fsS -X POST "$1" -H 'Content-Type: application/json' -d "$2"
}

json_id() {  # read JSON on stdin, print its "id"
  python3 -c 'import sys, json; print(json.load(sys.stdin)["id"])'
}

# Fail early with a clear message if the API isn't up.
if ! curl -fsS "${BASE_URL}/healthz" >/dev/null 2>&1; then
  echo "Error: API not reachable at ${BASE_URL}." >&2
  echo "Start it first:  flask --app app run" >&2
  exit 1
fi

# --- Manufacturers: "name|state" -------------------------------------------
manufacturers=(
  "Acme Corp|CA"
  "Globex|NY"
  "Initech|TX"
)

echo "Seeding ${#manufacturers[@]} manufacturers..."
manufacturer_ids=()
for entry in "${manufacturers[@]}"; do
  IFS='|' read -r name state <<< "$entry"
  id=$(post_json "${BASE_URL}/manufacturers" \
    "{\"name\": \"${name}\", \"state\": \"${state}\"}" | json_id)
  manufacturer_ids+=("$id")
  echo "  ${name} (${state}) -> id ${id}"
done

# --- Items: "name|description|price|manufacturer_index" ----------------------
# The last field indexes into manufacturer_ids above (0 = Acme, 1 = Globex, ...).
items=(
  "Widget|A small general-purpose widget|9.99|0"
  "Gadget|A more advanced gadget|19.95|0"
  "Sprocket|Toothed wheel, sold individually|2.50|1"
  "Cog|Replacement cog, fits most sprockets|1.25|1"
  "Gizmo|Does a bit of everything|49.00|2"
)

echo "Seeding ${#items[@]} items..."
for entry in "${items[@]}"; do
  IFS='|' read -r name description price mfr_index <<< "$entry"
  manufacturer_id="${manufacturer_ids[$mfr_index]}"
  post_json "${BASE_URL}/items" \
    "{\"name\": \"${name}\", \"description\": \"${description}\", \"price\": ${price}, \"manufacturer_id\": ${manufacturer_id}}"
  echo
done

echo "Done. Current items:"
curl -fsS "${BASE_URL}/items"
echo
