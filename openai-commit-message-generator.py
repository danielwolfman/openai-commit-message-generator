import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI, AuthenticationError

# Azure AD and Azure OpenAI configuration
AZURE_OPENAI_API_VERSION = '2024-06-01'
DEPLOYMENT_NAME = 'gpt-4-turbo'
SYSTEM_PROMPT = "You are a git diff summarizer. You get the git diff of a code change and generate a commit message that follows the commit style guide. you only send the summary, and nothing else."
ASSISTANT_PROMPT = "Based on the following code changes, generate a commit message that follows the commit style guide:\n\n"

# Load environment variables from .env file
load_dotenv()

# Retrieve the Azure OpenAI API key from the environment variables
API_KEY = os.getenv('API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')

client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=API_KEY
)

DEFAULT_STYLE_GUIDE = """
# Commit Style Guide

1. Start the commit message with the change kind (available kinds are: fix, feat, chore, ci, build, docs, style, refactor, perf, test, revert, note )
2. After the kind, write the a short summary of the changes (for example, "fix: a bugfix in component X regarding logging errors")
3. Use the imperative mood in the summary (e.g., "Add feature" instead of "Added feature").
4. Separate the summary from the body with a blank line.
5. Use the body to provide more detailed information about the changes.
6. Wrap the body at 72 characters per line.
7. Use bullet points for each change or feature added.
8. Use present tense in the body (e.g., "Fix bug" instead of "Fixed bug").
9. Refer to any filenames/filepaths in the bullet points, for more context.

"""

STYLE_GUIDE_FALLBACK_LOCATION = os.path.expanduser('~/commit_style_guide.md')

def read_style_guide():
    try:
        with open('COMMIT_STYLE.md', 'r') as f:
            commit_style_content = f.read()
            # Save the style guide to a fallback location
            with open(STYLE_GUIDE_FALLBACK_LOCATION, 'w') as fallback:
                fallback.write(commit_style_content)
            return commit_style_content
    except FileNotFoundError:
        try:
            with open(STYLE_GUIDE_FALLBACK_LOCATION, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return DEFAULT_STYLE_GUIDE

def get_assistant_prompt():
    return ASSISTANT_PROMPT + read_style_guide()

def chunk_diffs(diffs, max_tokens=3000):
    chunks = []
    token_multiplier = 1.5  # Approximation: Each word may roughly correspond to 1.5 tokens

    for _, file_diff in diffs.items():
        diff_tokens = int(len(file_diff.split()) * token_multiplier)
        
        # If a single file_diff exceeds the max token limit, split it into smaller parts
        if diff_tokens > max_tokens:
            words = file_diff.split()
            current_chunk = ""
            current_tokens = 0

            for word in words:
                word_tokens = int(len(word) * token_multiplier)

                if current_tokens + word_tokens > max_tokens:
                    chunks.append(current_chunk.strip())  # Finalize current chunk
                    current_chunk = word  # Start new chunk
                    current_tokens = word_tokens
                else:
                    current_chunk += ' ' + word
                    current_tokens += word_tokens

            if current_chunk:
                chunks.append(current_chunk.strip())  # Add the last remaining chunk
        else:
            chunks.append(file_diff)  # If within limits, add the entire diff

    return chunks

def generate_text_with_azure_openai(prompt):
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "assistant", "content": get_assistant_prompt()},
                {"role": "user", "content": prompt}
            ]
        )
    except AuthenticationError:
        print("Authentication error. Please check your Azure OpenAI API key.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    return response.choices[0].message.content

def summarize_chunk(chunk):
    return generate_text_with_azure_openai(chunk)

def combine_summaries(summaries):
    return '\n'.join(f"- {summary.strip()}" for summary in summaries)

def generate_final_commit_message(combined_summaries):
    prompt = f"Based on the summaries below, generate a commit message that follows the style guide:\n{combined_summaries}"
    return generate_text_with_azure_openai(prompt)

def main():
    all_diffs = sys.stdin.read()
    if not all_diffs.startswith('diff --git'):
        print("Not a valid git diff input. Please provide the git diff as input.", file=sys.stderr)
        sys.exit(1)

    # Chunk the diffs
    diff_chunks = chunk_diffs({'combined_diff': all_diffs})
    
    # Summarize each chunk
    summaries = []
    for chunk in diff_chunks:
        summary = summarize_chunk(chunk)
        summaries.append(summary)
    
    if len(summaries) > 1:
        # Combine summaries
        combined_summaries = combine_summaries(summaries)
        
        # Generate the final commit message
        commit_message = generate_final_commit_message(combined_summaries)
    else:
        commit_message = summaries[0]
    
    print(commit_message.strip())

if __name__ == '__main__':
    main()
