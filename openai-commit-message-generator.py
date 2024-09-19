import argparse
import os
import subprocess
import requests
import webbrowser
import time
import json
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Azure AD and Azure OpenAI configuration
TENANT_ID = 'some_tenant_id'  # Replace with your Azure AD Tenant ID
CLIENT_ID = 'some_client_id'  # Replace with your Azure AD Application (Client) ID
RESOURCE = 'https://some_resource'  # Replace with your Azure AD Application ID URI
AUTHORITY_URL = f'https://login.microsoftonline.com/{TENANT_ID}'
AUTH_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'
SCOPES = ['api://the_api_id/.default']
REDIRECT_URI = 'http://localhost:5000/getToken'
TOKEN_PATH = os.path.expanduser('~/.azure_openai_token.json')

# Azure OpenAI specific configuration
AZURE_OPENAI_ENDPOINT = 'https://some-azure-openai-endpoint.com'
AZURE_OPENAI_API_VERSION = '2024-06-01'
DEPLOYMENT_NAME = 'gpt-4-turbo'
MAX_TOKENS_PER_MINUTE = 10000  # 10,000 tokens per minute limit for GPT-4 Turbo

DEFAULT_STYLE_GUIDE = """
# Commit Style Guide

1. Start the commit message with a short summary of the changes.
2. Use the imperative mood in the summary (e.g., "Add feature" instead of "Added feature").
3. Separate the summary from the body with a blank line.
4. Use the body to provide more detailed information about the changes.
5. Wrap the body at 72 characters per line.
6. Use bullet points for each change or feature added.
7. Use present tense in the body (e.g., "Fix bug" instead of "Fixed bug").
8. Reference any relevant issues or tickets in the body.
9. Use the style guide consistently across commits.
10. Proofread the commit message before pushing to the repository.

"""
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/getToken':
            query_components = parse_qs(parsed_path.query)
            if 'code' in query_components:
                self.server.auth_code = query_components['code'][0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Authentication successful. You can close this window.')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Authentication failed.')
        else:
            self.send_response(404)
            self.end_headers()

def get_access_token():
    # Check if token exists and is valid
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as f:
            token_data = json.load(f)
        expires_at = token_data.get('expires_at', 0)
        if expires_at > time.time():
            return token_data['access_token']

    # Start local server to receive the auth code
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, OAuthHandler)

    # Build the authorization URL
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'response_mode': 'query',
        'scope': ' '.join(SCOPES)
    }
    auth_url = AUTHORITY_URL + AUTH_ENDPOINT + '?' + urlencode(params)

    # Open the browser for user login
    print('Opening browser for Azure login...')
    webbrowser.open(auth_url)

    # Wait for the auth code
    httpd.handle_request()
    auth_code = httpd.auth_code

    # Exchange auth code for access token
    token_data = get_token_from_code(auth_code)
    save_token(token_data)
    return token_data['access_token']

def get_token_from_code(auth_code):
    post_data = {
        'client_id': CLIENT_ID,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }
    token_url = AUTHORITY_URL + TOKEN_ENDPOINT
    response = requests.post(token_url, data=post_data)
    response.raise_for_status()
    token_data = response.json()
    token_data['expires_at'] = time.time() + int(token_data['expires_in'])
    return token_data

def save_token(token_data):
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f)

def read_style_guide():
    try:
        with open('COMMIT_STYLE.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return DEFAULT_STYLE_GUIDE

def get_changed_files(staged_only):
    cmd = ["git", "status", "--porcelain"]
    if staged_only:
        cmd.append("--untracked-files=no")
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    files = {'added': [], 'modified': [], 'deleted': []}
    for line in lines:
        if not line:
            continue
        status, file = line[:2], line[3:]
        if 'A' in status:
            files['added'].append(file)
        elif 'M' in status:
            files['modified'].append(file)
        elif 'D' in status:
            files['deleted'].append(file)
    return files

def get_file_diffs(files, staged_only):
    diffs = {}
    diff_cmd = ["git", "diff"]
    if staged_only:
        diff_cmd.append("--staged")
    for file in files['modified']:
        cmd = diff_cmd + [file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        diffs[file] = result.stdout
    return diffs

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
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': prompt,
        'max_tokens': 150,
        'temperature': 0.7,
        'n': 1,
    }
    response = requests.post(
        f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/completions?api-version={AZURE_OPENAI_API_VERSION}",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()['choices'][0]['text']

def summarize_chunk(chunk):
    prompt = f"Summarize the following code changes:\n\n{chunk}"
    return generate_text_with_azure_openai(prompt)

def combine_summaries(summaries):
    return '\n'.join(f"- {summary.strip()}" for summary in summaries)

def generate_final_commit_message(style_guide, combined_summaries):
    prompt = f"{style_guide}\n\nBased on the summaries below, generate a commit message that follows the style guide:\n{combined_summaries}"
    return generate_text_with_azure_openai(prompt)

def parse_args():
    parser = argparse.ArgumentParser(description='Generate a commit message using Azure OpenAI.')
    parser.add_argument('--staged', action='store_true', help='Summarize only staged files.')
    return parser.parse_args()

def main():
    args = parse_args()
    style_guide = read_style_guide()
    files = get_changed_files(staged_only=args.staged)
    diffs = get_file_diffs(files, staged_only=args.staged)
    
    # Combine diffs into one text
    all_diffs = '\n'.join(diffs.values())
    
    # Chunk the diffs
    diff_chunks = chunk_diffs({'combined_diff': all_diffs})
    
    # Summarize each chunk
    summaries = []
    for chunk in diff_chunks:
        summary = summarize_chunk(chunk)
        summaries.append(summary)
    
    # Combine summaries
    combined_summaries = combine_summaries(summaries)
    
    # Generate the final commit message
    commit_message = generate_final_commit_message(style_guide, combined_summaries)
    
    print("Generated Commit Message:\n")
    print(commit_message.strip())

if __name__ == '__main__':
    main()
