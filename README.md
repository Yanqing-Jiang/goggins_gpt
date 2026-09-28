<p align="center"><img src="david_goggins.jpg" alt="Goggins GPT avatar" width="120"></p>

<h1 align="center">Goggins GPT</h1>

<p align="center"><b>A motivational chat persona that answers in text and in a synthesized voice.</b><br>
This repository is the original August 2023 prototype, built with Streamlit, LangChain, OpenAI and ElevenLabs.</p>

<p align="center">
<a href="https://yanqing.app/project/goggins-gpt/"><b>Explore Goggins GPT on yanqing.app</b></a> ·
<a href="#how-it-works">How it works</a> ·
<a href="#run-it-locally">Run it locally</a> ·
<a href="#legacy-constraints">Legacy constraints</a>
</p>

---

## Current experience vs. this repo

The project continues on yanqing.app, but on a different stack. This code is the earlier version, not the current one.

| | yanqing.app project page | This repository |
|---|---|---|
| Stack | React, FastAPI, Gemini, ElevenLabs | Streamlit, LangChain, OpenAI, ElevenLabs |
| Status | Current portfolio experience | Legacy source snapshot from August 2023 |
| Best for | Trying Goggins GPT | Reading or reviving the original code |

The first README linked to a Streamlit Community Cloud deployment at [goggins-gpt.streamlit.app](https://goggins-gpt.streamlit.app). That link stays here for reference only. Its availability has not been verified.

## How it works

1. You type a message into `st.text_input`.
2. `get_response_from_ai` wraps it in a short persona prompt and runs a LangChain `LLMChain` on `gpt-3.5-turbo-16k-0613` with temperature 0.2.
3. The reply appears next to `david_goggins.jpg`.
4. `get_voice_message` sends the reply to ElevenLabs text-to-speech, writes the stream to `output.mp3`, and plays it with `st.audio`.
5. `log_to_db` writes the message, the reply, the project name and a timestamp to `[dbo].[gpt_exp_retrieval]` on SQL Server.

A new `ConversationBufferWindowMemory(k=2)` gets created on every call, so replies don't remember earlier turns, even though the code includes a memory object.

## Run it locally

Before launching, configure the services below and resolve the dependency and model compatibility issues in [Legacy constraints](#legacy-constraints). The commands show the entrypoint; they are not a verified modern environment.

The entrypoint is `goggins_gpt.py`. You need:

- Python in a separate virtual environment
- Microsoft **ODBC Driver 17 for SQL Server** (the driver name is hardcoded)
- A SQL Server database you can reach, with the logging table below
- An OpenAI API key and an ElevenLabs API key

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt requests
export OPENAI_API_KEY="<your-openai-key>"
streamlit run goggins_gpt.py
```

The app reads the rest of its settings from `.streamlit/secrets.toml`. Don't commit that file.

```toml
ELEVEN_LABS_API_KEY = "<your-elevenlabs-key>"
server = "<sql-server-host>"
database = "<database-name>"
username = "<sql-user>"
password = "<sql-password>"
```

The repo doesn't define column types for the logging table. This example schema matches the four fields used by the insert; adapt it to your database:

```sql
CREATE TABLE dbo.gpt_exp_retrieval (
    user_message  NVARCHAR(MAX),
    output_result NVARCHAR(MAX),
    project_used  NVARCHAR(100),
    log_time      DATETIME2
);
```

## Legacy constraints

| Area | What to expect |
|---|---|
| Dependencies | `requirements.txt` has no version pins. It also leaves out `requests`, which the code imports. The imports (`langchain.chat_models`, `langchain.memory`, `LLMChain`) date from 2023, so use a compatible dependency set or migrate the imports before running it. |
| OpenAI model | `gpt-3.5-turbo-16k-0613` is a legacy snapshot. Change `model=` in `goggins_gpt.py` to a model your account can use. |
| Voice | The voice ID `UzKqcDbzCrsH0d6BBKa8` and the model `eleven_monolingual_v1` are hardcoded. The voice was trained in the author's ElevenLabs VoiceLab, so you will probably need your own voice ID. The code doesn't check the HTTP status, so an API error gets written into `output.mp3`. |
| Audio file | Every reply overwrites the same `output.mp3` in the working directory. All sessions share that one file. |
| Logging | SQL logging always runs. Every message and reply is stored. If the database connection fails, you get an error after the reply is shown. |
| Memory | No chat history carries over between turns (see above). |

## Files

| File | Purpose |
|---|---|
| [`goggins_gpt.py`](goggins_gpt.py) | Streamlit app: prompt, LLM call, text-to-speech, SQL logging |
| [`requirements.txt`](requirements.txt) | Unpinned dependency list (incomplete, see above) |
| [`david_goggins.jpg`](david_goggins.jpg) | Avatar shown next to each reply |
| [`voice_sample.mp3`](voice_sample.mp3) | Audio sample included in the repo; the app doesn't use it |

## Usage note

This is a personal tribute project, not for commercial use. The repository has no license file.
