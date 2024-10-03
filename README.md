# Git Diff Summarizer with Azure OpenAI

This project leverages the Azure OpenAI API to automatically generate commit messages from Git diffs. The script reads the diff output of code changes, processes it by chunking large diffs, and uses Azure OpenAI's model to generate concise commit messages that follow a predefined style guide.

## Features

- **Environment Configuration**: Supports loading API keys and other environment variables from a `.env` file.
- **Chunking**: Automatically splits large diffs into smaller parts for processing.
- **Commit Message Generation**: Generates commit messages that adhere to a style guide, using Azure OpenAI.
- **Customizable Style Guide**: Reads the commit style guide from a file (`COMMIT_STYLE.md`) or falls back to a default guide if none is found.

## Requirements

- Python 3.6+
- The following Python libraries:
  - `python-dotenv`
  - `openai`
  
You can install these dependencies using:

```bash
pip install python-dotenv openai
```

## Setup

1. **Environment Variables**: Create a `.env` file in the root directory with the following content:

   ```
   API_KEY=<Your_Azure_OpenAI_API_Key>
   RESOURCE=<Your_Azure_OpenAI_Resource_Endpoint>
   ```

2. **COMMIT_STYLE.md** (Optional): Create a file named `COMMIT_STYLE.md` to define your custom commit message style guide. If not provided, a default guide will be used.

## Usage

**Run the Script**: Pipe a git diff to the script and it will generate a commit message for the provided diff.

   Example:

   ```bash
   git diff | python git_diff_summarizer.py
   ```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
