"""Demo script: query Flipside for a small resultset, then ask an LLM to summarize or extract narratives.

Usage:
  export FLIPSIDE_API_KEY=...
  export OPENAI_API_KEY=... (or ANTHROPIC_API_KEY)
  python -m fluxo.backend.scripts.llm_flipside_demo

This script is intentionally simple and blocking; it demonstrates how you might wire the two services.
"""
from __future__ import annotations
import os
from pprint import pprint

from fluxo.backend.services.flipside_api import run_sql_and_get_results, FlipsideError
from fluxo.backend.services.llm_providers import LLMClient, LLMError

SAMPLE_SQL = """
SELECT block_timestamp, event_name, tx_hash
FROM flipside_prod_db.ethereum.events
ORDER BY block_timestamp DESC
LIMIT 5
"""


def main():
    llm = LLMClient()
    try:
        print("Running Flipside query...")
        flipside_res = run_sql_and_get_results(SAMPLE_SQL)
        pprint(flipside_res)
    except FlipsideError as e:
        print("Flipside query failed:", e)
        return

    # Construct a short prompt summarizing the result
    rows = flipside_res.get("results") or flipside_res.get("rows") or flipside_res.get("data")
    if not rows:
        print("No rows found in Flipside response; exiting")
        return

    text_summary = "Here are the top rows from Flipside:\n"
    for r in rows[:5]:
        text_summary += str(r) + "\n"

    prompt = (
        "You are an on-chain analyst assistant. Summarize the following rows and extract any short narratives "
        "or anomalies (one-sentence each):\n\n" + text_summary
    )

    # Try OpenAI/GPT first, then fall back to Claude
    try:
        print("Calling OpenAI to summarize...")
        resp = llm.call_openai(prompt)
        # extract text (best-effort)
        choices = resp.get("choices") or []
        if choices:
            content = choices[0].get("message", {}).get("content") or choices[0].get("text")
            print("OpenAI summary:\n", content)
        else:
            pprint(resp)
    except LLMError as e:
        print("OpenAI failed, trying Claude...", e)
        try:
            resp = llm.call_claude(prompt)
            # Anthropic response shape varies; try to pull `completion`/`output` fields
            text = resp.get("completion") or resp.get("output") or resp.get("text") or str(resp)
            print("Claude summary:\n", text)
        except LLMError as e2:
            print("Both LLM calls failed:", e2)

