# OpenAI Commit Message Generator

A Python script that generates commit messages based on git diffs using Azure OpenAI's GPT models, following a customizable commit style guide.

## Introduction

Writing detailed and well-formatted commit messages is crucial for maintaining a clear project history. The OpenAI Commit Message Generator simplifies this process by automatically generating commit messages based on your git diffs. It leverages Azure OpenAI's GPT models to produce concise and structured commit messages that adhere to a specified style guide.

## Features

- **Automated Commit Message Generation**: Generates commit messages by summarizing git diffs.
- **Customizable Style Guide**: Follows a commit style guide that can be customized to your preferences.
- **Azure OpenAI Integration**: Utilizes Azure OpenAI services for advanced text generation.
- **Handles Large Diffs**: Automatically chunks large diffs to comply with model token limits.

## Prerequisites

- **Python**: Version 3.6 or higher.
- **Azure Subscription**: Access to Azure OpenAI services.
- **Git**: Installed and configured on your system.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/danielwolfman/openai-commit-message-generator.git
   cd openai-commit-message-generator
   ```

2. **Install Dependencies**

   Install the required Python packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Azure OpenAI Setup

Before using the script, you need to configure it to communicate with Azure OpenAI services.

1. **Obtain Azure OpenAI Credentials**

   - **Azure OpenAI Endpoint**: This is your Azure OpenAI resource endpoint, typically in the format `https://<your-resource-name>.openai.azure.com/`.
   - **API Version**: The version of the Azure OpenAI API you are using (e.g., `2023-06-01-preview`).
   - **OpenAI Model Name**: The name of the model you wish to use (e.g., `gpt-4`, `gpt-3.5-turbo`).

2. **Set Environment Variables**

   Create a `.env` file in the root directory of the project or set the following environment variables:

   ```bash
   AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>
   AZURE_OPENAI_API_VERSION=<your-api-version>
   OPENAI_MODEL=<model-name>
   OPENAI_MODEL_MAX_TOKENS=<max-tokens>
   ```

   **Example `.env` File:**

   ```bash
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2023-06-01-preview
   OPENAI_MODEL=gpt-4
   OPENAI_MODEL_MAX_TOKENS=8192
   ```

   The script uses the `python-dotenv` package to load these variables.

3. **Azure Authentication**

   The script uses Azure's `DefaultAzureCredential` for authentication. Ensure that you are authenticated with Azure CLI or have set up the appropriate environment variables for Azure authentication.

   - **Azure CLI Authentication**: Log in using `az login`.
   - **Environment Variables**: Set `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET`.

### Commit Style Guide

You can customize the commit style guide to match your project's conventions.

1. **Create a Style Guide File**

   - Create a file named `COMMIT_STYLE.md` in the root directory of the project.
   - Alternatively, place a `~/.commit_style_guide.md` file in your home directory.

2. **Define Your Style Guide**

   **Example `COMMIT_STYLE.md`:**

   ```markdown
   # Commit Style Guide

   1. Start the commit message with a capitalized verb (e.g., "Add", "Fix").
   2. Use the present tense (e.g., "Add feature" not "Added feature").
   3. Keep the subject line under 50 characters.
   4. Separate the subject from the body with a blank line.
   5. Provide a detailed description in the body.
   6. Reference related issues or pull requests at the end.
   ```

3. **Fallback Style Guide**

   If no custom style guide is provided, the script uses a default style guide defined within the code.

### Caching Configuration

The script caches Azure OpenAI configuration in a file located at `~/.azure_openai_cache` for quicker access in subsequent runs. This cache file stores:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `OPENAI_MODEL`
- `OPENAI_MODEL_MAX_TOKENS`

If you update your environment variables, the cache file will be updated automatically.

## Usage

The script reads git diffs from standard input and outputs a formatted commit message to standard output.

### Basic Usage

1. **Navigate to Your Git Repository**

   ```bash
   cd /path/to/your/git/repository
   ```

2. **Stage Your Changes**

   ```bash
   git add .
   ```

3. **Generate and Use the Commit Message**

   ```bash
   git diff --cached | python openai-commit-message-generator.py > COMMIT_MSG.txt
   git commit -F COMMIT_MSG.txt
   ```

   Or, in a single command:

   ```bash
   git commit -a -m "$(git diff --cached | python /path/to/openai-commit-message-generator.py)"
   ```

### Handling Large Diffs

The script automatically chunks large diffs to comply with the model's maximum token limit. No additional action is required from the user.

### Examples

**Example 1**: Generate a commit message for unstaged changes.

```bash
git diff | python openai-commit-message-generator.py
```

**Example 2**: Generate a commit message and save it to a file.

```bash
git diff --cached | python openai-commit-message-generator.py > COMMIT_MSG.txt
```

**Example 3**: Commit changes using the generated message.

```bash
git commit -a -m "$(git diff | python openai-commit-message-generator.py)"
```

## Troubleshooting

- **Authentication Error**: If you encounter an `AuthenticationError`, ensure your Azure credentials are correctly set up and you have access to the OpenAI service.

- **Azure OpenAI Endpoint Not Found**: Verify that `AZURE_OPENAI_ENDPOINT` and other required environment variables are set either in your environment or in a `.env` file.

- **Invalid Git Diff Input**: Ensure you are providing a valid git diff. The script expects input starting with `diff --git`.

- **Missing Dependencies**: If you receive import errors, ensure all dependencies are installed via `pip install -r requirements.txt`.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

1. **Fork the Repository**

   ```bash
   git clone https://github.com/danielwolfman/openai-commit-message-generator.git
   ```

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -am 'Add new feature'
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI**: For providing powerful language models.
- **Azure**: For making AI services accessible.
- **Contributors**: Thanks to all contributors who have helped improve this project.
