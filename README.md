# Git Commit Message Generator CLI Tool

A cross-platform command-line interface (CLI) tool that generates commit messages by summarizing your Git diffs using the OpenAI GPT API. The commit messages adhere to a style guide specified in a `.md` file (e.g., `COMMIT_STYLE.md`) located in your project.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
  - [Options](#options)
- [Example](#example)
- [Notes and Considerations](#notes-and-considerations)
- [License](#license)

## Features

- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux.
- **Customizable Style Guide**: Uses a project-specific commit message style guide.
- **Selective Summarization**: Option to summarize only staged files.
- **Comprehensive Change Analysis**:
  - Lists all changed files (added, modified, deleted).
  - Inspects modified files to minimize API token usage.
  - Considers added and deleted files in the commit message.
- **OpenAI GPT Integration**: Leverages the OpenAI GPT API to generate natural language summaries.

## Prerequisites

- **Python**: Version 3.7 or higher.
- **Git**: Ensure Git is installed and accessible from the command line.
- **OpenAI API Key**: You need an API key from OpenAI. [Sign up here](https://beta.openai.com/signup/) if you don't have one.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/git-commit-message-generator.git
   cd git-commit-message-generator
   ```

2. **Install Python Packages**

   Install the required Python packages using `pip`:

   ```bash
   pip install openai argparse
   ```

3. **Make the Script Executable**

   (Optional) If you're on a Unix-like system, make the script executable:

   ```bash
   chmod +x generate_commit_message.py
   ```

## Setup

### 1. Create a Commit Message Style Guide

Create a `COMMIT_STYLE.md` file at the root of your project. This file should contain your commit message style guidelines.

**Example `COMMIT_STYLE.md`:**

```markdown
# Commit Message Style Guide

- **Subject Line**: Use the imperative mood (e.g., "Add feature" not "Added feature").
- **Length**: Limit the subject line to 72 characters.
- **Separation**: Separate the subject from the body with a blank line.
- **Body Content**: Use the body to explain the **what** and **why** of the changes.
- **Bullet Points**: Use bullet points for multiple changes.
```

### 2. Configure Your OpenAI API Key

You can provide your OpenAI API key in two ways:

- **As a Command-Line Argument**: Pass the `--api-key` argument when running the script.
- **As an Environment Variable**: Set the `OPENAI_API_KEY` environment variable.

**Setting the Environment Variable:**

- **Unix/MacOS**

  ```bash
  export OPENAI_API_KEY='your-api-key-here'
  ```

- **Windows Command Prompt**

  ```cmd
  set OPENAI_API_KEY=your-api-key-here
  ```

- **Windows PowerShell**

  ```powershell
  $env:OPENAI_API_KEY="your-api-key-here"
  ```

## Usage

Run the script from the root directory of your Git repository.

```bash
python generate_commit_message.py [options]
```

### Options

- `--staged`: Summarize only staged files.
- `--api-key`: Provide your OpenAI API key directly.
- `-h`, `--help`: Show the help message and exit.

**Examples:**

- **Summarize All Changes**

  ```bash
  python generate_commit_message.py --api-key your-api-key-here
  ```

- **Summarize Only Staged Changes**

  ```bash
  python generate_commit_message.py --staged --api-key your-api-key-here
  ```

- **Using Environment Variable for API Key**

  ```bash
  python generate_commit_message.py
  ```

## Example

**Command:**

```bash
python generate_commit_message.py --staged
```

**Output:**

```
Generated Commit Message:

Add feature to generate commit messages using OpenAI GPT API

- Implement CLI tool to automatically generate commit messages
- Fetch and analyze git diffs for modified files
- Include added and deleted files in the commit summary
- Adhere to the commit message style guide specified in COMMIT_STYLE.md
```

## Notes and Considerations

- **API Key Security**: Never expose your OpenAI API key in public repositories or shared environments.
- **Token Limits**: The OpenAI GPT models have a token limit. For large diffs, the script may need to truncate or summarize the content to stay within the limit.
- **Error Handling**: The script includes basic error handling but can be extended for robustness.
- **Performance**: Generating commit messages may take a few seconds, depending on the size of the changes and network latency.
- **Customization**: Feel free to modify the script to suit your specific needs, such as changing the OpenAI model or adjusting the prompt.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*For any issues or contributions, please open an issue or submit a pull request on the GitHub repository.*
