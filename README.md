# politbench

Checks where a local model lands on Political Compass and 10Groups.

## install

Python 3.8+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## run

Start your local model server first, then run one of these:

```bash
python evaluate.py
python evaluate.py --test both
python evaluate.py --test 10groups
python evaluate_tui.py
```

`python evaluate.py` defaults to the compass test.

Default API URL:

```text
http://localhost:2325/v1/chat/completions
```

Useful flags:

```text
--url URL
--model MODEL
--test compass|10groups|both
--output FILE
--system-prompt "prefix text"
```

Use `--verbose` with `evaluate.py` if you want to see every question.

Results are written to `evaluation_results.json` unless you set `--output`.

Compass gives you economic/social scores. 10Groups gives you the full axis breakdown.

## notes

- works with OpenAI-compatible local endpoints
- TUI version uses `rich`
- questions come from Political Compass and 10Groups

## license

MIT
