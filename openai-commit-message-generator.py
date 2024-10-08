import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI, AuthenticationError
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# OpenAI configuration
SYSTEM_PROMPT = "You are a git diff summarizer. You get the git diff of a code change and generate a commit message that follows the commit style guide. you only send the summary, and nothing else."
ASSISTANT_PROMPT = "Based on the following code changes, generate a commit message that follows the commit style guide:\n\n"

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

def read_style_guide():
    style_guide_fallback_location = os.path.expanduser('~/.commit_style_guide.md')
    try:
        with open('COMMIT_STYLE.md', 'r') as f:
            commit_style_content = f.read()
            # Save the style guide to a fallback location
            with open(style_guide_fallback_location, 'w') as fallback:
                fallback.write(commit_style_content)
            return commit_style_content
    except FileNotFoundError:
        try:
            with open(style_guide_fallback_location, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return DEFAULT_STYLE_GUIDE
        
def get_azure_openai_cache():
    load_dotenv()
    azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
    openai_model = os.getenv('OPENAI_MODEL')
    openai_model_max_tokens = int(os.getenv('OPENAI_MODEL_MAX_TOKENS', 8192))
    azure_openai_cache_location = os.path.expanduser('~/.azure_openai_cache')
    if azure_openai_endpoint:
        # If cache doesn't exist, create it
        if not os.path.exists(azure_openai_cache_location):
            with open(azure_openai_cache_location, 'w') as f:
                f.write(f'AZURE_OPENAI_ENDPOINT={azure_openai_endpoint}\n')
                f.write(f'AZURE_OPENAI_API_VERSION={azure_openai_api_version}\n')
                f.write(f'OPENAI_MODEL={openai_model}\n')
                f.write(f'OPENAI_MODEL_MAX_TOKENS={openai_model_max_tokens}\n')
        return azure_openai_endpoint, azure_openai_api_version, openai_model, openai_model_max_tokens
    try:
        with open(azure_openai_cache_location, 'r') as f:
            for line in f:
                if line.startswith('AZURE_OPENAI_ENDPOINT'):
                    azure_openai_endpoint = line.split('=')[1].strip()
                    if not azure_openai_endpoint:
                        print("Azure OpenAI endpoint not found. Please provide them in the environment variables or in the cache file.", file=sys.stderr)
                        sys.exit(1)
                elif line.startswith('AZURE_OPENAI_API_VERSION'):
                    azure_openai_api_version = line.split('=')[1].strip()
                    if not azure_openai_api_version:
                        print("Azure OpenAI API version not found. Please provide them in the environment variables or in the cache file.", file=sys.stderr)
                        sys.exit(1)
                elif line.startswith('OPENAI_MODEL_MAX_TOKENS'):
                    try:
                        openai_model_max_tokens = int(line.split('=')[1].strip())
                        if openai_model_max_tokens <= 0:
                            print(f"Warning: Invalid OPENAI_MODEL_MAX_TOKENS value in the cache file: {azure_openai_cache_location}. Using the default value of 8192.", file=sys.stderr)
                            openai_model_max_tokens = 8192
                    except ValueError:
                        openai_model_max_tokens = 8192
                        print(f"Warning: Invalid OPENAI_MODEL_MAX_TOKENS value in the cache file: {azure_openai_cache_location}. Using the default value of 8192.", file=sys.stderr)
                elif line.startswith('OPENAI_MODEL'):
                    openai_model = line.split('=')[1].strip()
                    if not openai_model:
                        print("OpenAI model not found. Please provide them in the environment variables or in the cache file.", file=sys.stderr)
                        sys.exit(1)
        return azure_openai_endpoint, azure_openai_api_version, openai_model, openai_model_max_tokens
    except FileNotFoundError:
        print("Azure OpenAI endpoint not found. Please provide them in the environment variables or in the cache file.", file=sys.stderr)
        sys.exit(1)

azure_openai_endpoint, api_version, openai_model, openai_model_max_tokens = get_azure_openai_cache()
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

# print(f"Using Azure OpenAI endpoint: {azure_openai_endpoint}, api version: {api_version}", file=sys.stderr)
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_openai_endpoint,
    azure_ad_token_provider=token_provider
)

def get_assistant_prompt():
    return ASSISTANT_PROMPT + read_style_guide()

def chunk_diffs(diffs):
    chunks = []
    token_multiplier = 1.5  # Approximation: Each word may roughly correspond to 1.5 tokens

    for _, file_diff in diffs.items():
        diff_tokens = int(len(file_diff.split()) * token_multiplier)
        
        # If a single file_diff exceeds the max token limit, split it into smaller parts
        if diff_tokens > openai_model_max_tokens:
            words = file_diff.split()
            current_chunk = ""
            current_tokens = 0

            for word in words:
                word_tokens = int(len(word) * token_multiplier)

                if current_tokens + word_tokens > openai_model_max_tokens:
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
        # print(f"Generating commit message using model {openai_model}...", file=sys.stderr)
        response = client.chat.completions.create(
            model=openai_model,
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
