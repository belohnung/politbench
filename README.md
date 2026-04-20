# Political Stance Evaluator for Local AI Models

A small Python tool for probing the political stance of local AI models using questions from **The Political Compass** and **10Groups**.

## What this repository contains

- `evaluate.py` - command-line evaluator for Political Compass, 10Groups, or both
- `evaluate_tui.py` - terminal UI with live progress and visualizations
- `requirements.txt` - Python dependencies for the project
- `LICENSE` - MIT license for the project

## Features

- **CLI Mode**: Simple command-line evaluation with verbose output option
- **TUI Mode**: Real-time evaluation with live compass visualization and question log
- **Political Compass Test**: 2D evaluation (Economic Left/Right, Social Libertarian/Authoritarian)
- **10Groups Test**: 22-axis comprehensive political evaluation
- Support for OpenAI-compatible API endpoints
- ASCII art visualizations
- Detailed JSON output with all responses
- Works with any local LLM running an HTTP API (llama.cpp, Ollama, LM Studio, etc.)

## Requirements

- Python 3.8+
- A running local AI model with an HTTP API endpoint

Install dependencies with:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

### 1. Start your local AI model

Make sure your local model is running and accessible. Common setups:

**llama.cpp server:**
```bash
./server -m model.gguf --port 2325
```

**Ollama:**
```bash
# Start Ollama server
ollama serve
# In another terminal, run a model
ollama run llama3
```

**LM Studio:**
Enable the local server on port 2325 (or your preferred port).

### 2. Run the evaluation

#### CLI Mode (Simple)
```bash
# Default: Political Compass test only
python evaluate.py

# Run both tests
python evaluate.py --test both

# Run 10Groups only
python evaluate.py --test 10groups

# With verbose output (shows each question)
python evaluate.py --verbose

# Custom URL and model name
python evaluate.py --url http://localhost:1234/v1/chat/completions --model llama3

# Save to custom file
python evaluate.py --output my_results.json
```

#### TUI Mode (Visual)
```bash
# Interactive TUI with live compass and question log
python evaluate_tui.py --url http://localhost:2325/v1/chat/completions

# With custom model name
python evaluate_tui.py --model llama3
```

The TUI shows:
- **Left side**: Live log of questions and responses with color-coded stances
- **Right side**: Real-time updating political compass with your position
- **Progress bar**: Shows evaluation progress
- **Current scores**: Live-updated economic and social scores
- **Quadrant identification**: Libertarian Left, Authoritarian Right, etc.

## Usage Options

### CLI Mode (`evaluate.py`)

```
python evaluate.py [OPTIONS]

Options:
  --url URL           API endpoint (default: http://localhost:2325/v1/chat/completions)
  --model MODEL       Model name for API requests (default: local)
  --test {compass,10groups,both}
                      Which test to run (default: compass)
  --verbose, -v       Show progress for each question
  --output FILE, -o   Save results to JSON file (default: evaluation_results.json)
  --help              Show help message
```

### TUI Mode (`evaluate_tui.py`)

```
python evaluate_tui.py [OPTIONS]

Options:
  --url URL           API endpoint (default: http://localhost:2325/v1/chat/completions)
  --model MODEL       Model name for API requests (default: local)
  --test {compass,10groups,both}
                      Which test to run (default: compass)
  --output FILE, -o   Save results to JSON file (default: evaluation_results.json)
  --help              Show help message
```

Both CLI and TUI modes support:

```
  --system-prompt TXT Optional system prompt prefix for persona testing
```

## Understanding the Results

### Political Compass

- **Economic Axis** (-10 to +10): Left (negative) to Right (positive)
- **Social Axis** (-10 to +10): Libertarian (negative) to Authoritarian (positive)

The four quadrants:
- **Libertarian Left**: Personal freedom + economic equality
- **Authoritarian Left**: State control + economic equality  
- **Libertarian Right**: Free markets + personal freedom
- **Authoritarian Right**: Free markets + traditional values

### 10Groups

22 different axes covering:
- Economic views (Regulation, System)
- Government structure (System, Size)
- Diplomatic views (Applicability, Relations)
- Societal values (Tradition, Change)
- Technology stance (Acceleration, Transhumanism)
- Legal philosophy (System, Focus)
- Cultural views (Hierarchy, Assimilation)
- Procedural views (Compromise, Transition)
- Political style (Extremism, Engagement)
- Philosophical (Collectivization, Revolution, Idealism, Consequence)

## Example Output

### CLI Mode

```
Political Stance Evaluation
============================================================
Target URL: http://localhost:2325/v1/chat/completions
Model: local
Test: both

============================================================
RUNNING POLITICAL COMPASS TEST
============================================================
Evaluating AI model at http://localhost:2325/v1/chat/completions...
Asking 60 questions...

============================================================
POLITICAL COMPASS RESULTS
============================================================

Economic Score: -3.50 (Left: -10, Right: +10)
Social Score:   -2.80 (Libertarian: -10, Authoritarian: +10)

Quadrant: Libertarian Left
Description: Favors personal freedom and economic equality
Historical examples: Ghandi, Nelson Mandela, Dalai Lama

============================================================
VISUALIZATION
============================================================
               ECONOMIC AXIS
        <-Left                  Right->

......................^....................  LIBERTARIAN
......................|....................
......................|....................
......................|....................
...................X..|....................
......................|....................
<---------------------+-------------------->  SOCIAL AXIS
......................|....................
......................v....................  AUTHORITARIAN

  X = Model position (-3.5, -2.8)

Detailed results saved to: evaluation_results.json
```

### TUI Mode

The TUI provides a real-time interface:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🏛️  Political Compass Evaluation | Model: llama3 | ...    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─ 📋 Question Log ─────────────────────────────────────────┐ ┌─ 🧭 Political Compass ──────────────────────────────────┐
│ [████████████████████████░░░░░░░░░░░░░░░░░░░░] 36/60      │ │                                                           │
│                                                           │ │     ECONOMIC AXIS                                       │
│ [36] DISAGREE       | Corporations cannot be trusted t... │ │ <-Left         Right->                                  │
│ [35] STRONGLY_AGREE | An autocracy is more beneficial...  │ │                                                           │
│ [34] NEUTRAL        | It's important that we maintain... │ │              ^                   LIBERTARIAN            │
│ ...                                                       │ │              |                                          │
│ [21] AGREE          | Freedom of business is the best...  │ │              |                                          │
│                                                           │ │      X       |                                          │
│                                                           │ │              |                                          │
│                                                           │ │ <------------+------------>  SOCIAL AXIS                │
│                                                           │ │              |                                          │
│                                                           │ │              |                                          │
│                                                           │ │              |                                          │
│                                                           │ │              v                   AUTHORITARIAN           │
│                                                           │ │                                                           │
│                                                           │ │ Quadrant: [cyan]Libertarian Left[/cyan]                          │
│                                                           │ │                                                           │
│                                                           │ │ Progress: 36/60 questions                               │
└───────────────────────────────────────────────────────────┘ └───────────────────────────────────────────────────────────┘

╭──────────┬───────┬──────────────────────╮
│ Axis     │ Score │ Position             │
├──────────┼───────┼──────────────────────┤
│ Economic │ -4.58 │ Left                 │
│ Social   │ -5.28 │ Libertarian          │
╰──────────┴───────┴──────────────────────╯
```

## Output Format

The JSON output contains:
```json
{
  "api_url": "http://localhost:2325/v1/chat/completions",
  "model": "local",
  "test": "compass",
  "scores": {
    "economic": -4.58,
    "social": -5.28
  },
  "responses": [
    {
      "id": 1,
      "question": "If economic globalisation is inevitable...",
      "stance": "DISAGREE",
      "effects": {"economic": -2}
    }
  ]
}
```

## Troubleshooting

### Connection refused
Make sure your local model server is running and accessible at the specified URL.

Check with:
```bash
curl http://localhost:2325/v1/models
```

### No responses or all neutral
- Check that the API endpoint is correct
- Verify the model is loaded and ready
- Try increasing timeout in the code (default is 30 seconds)
- Some models may need `--model` set to the actual model name

### Different API formats
The script tries multiple API formats. If your model uses a different format, you may need to modify `get_model_response()` in the evaluator files.

### Rich library not found (TUI mode)
```bash
pip install rich
```

## License

MIT. See [`LICENSE`](LICENSE).

## Credits

- Questions from [The Political Compass](https://www.politicalcompass.org/)
- Questions from [10Groups](https://10groups.github.io/)
- TUI powered by [Rich](https://github.com/Textualize/rich)
