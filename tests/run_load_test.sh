#!/usr/bin/env bash
# Load test: start the fake LLM and the backend, run 30 learners, stop everything.
# Run from backend/:  bash tests/run_load_test.sh
set -e
export APP_ENV=.env.test   # used by the backend and the test
PY=.venv/bin/python        # the servers run directly, so kill reaches them (uv run would sit in between)

# refuse to run if another backend (e.g. make dev) already uses the port
if curl -s localhost:8000/ > /dev/null; then
  echo "Port 8000 is busy. Stop the other backend first."
  exit 1
fi

$PY -m tests.fake_llm &
FAKE=$!
$PY -m uvicorn app.main:app --port 8000 &
API=$!
trap 'kill $FAKE $API 2>/dev/null; wait' EXIT   # stop both servers and wait until they're gone

echo "Waiting for the backend..."
until curl -s localhost:8000/ > /dev/null; do sleep 0.5; done

uv run python -m tests.test_heavy_load