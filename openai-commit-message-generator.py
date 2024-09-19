import subprocess
import openai
import argparse

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

def read_style_guide():
    with open('COMMIT_STYLE.md', 'r') as f:
        style_guide = f.read()
    return style_guide

def construct_prompt(style_guide, files, diffs):
    prompt = f"{style_guide}\n\n"
    prompt += "Changes Summary:\n"
    if files['added']:
        prompt += "Added files:\n" + "\n".join(f"- {file}" for file in files['added']) + "\n"
    if files['deleted']:
        prompt += "Deleted files:\n" + "\n".join(f"- {file}" for file in files['deleted']) + "\n"
    prompt += "Modified files:\n"
    for file, diff in diffs.items():
        prompt += f"\nFile: {file}\nDiff:\n{diff}\n"
    prompt += "\nGenerate a commit message following the style guide above."
    return prompt

def generate_commit_message(prompt, api_key):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine='text-davinci-003',  # Use the appropriate model
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None,
    )
    message = response.choices[0].text.strip()
    return message

def parse_args():
    parser = argparse.ArgumentParser(description='Generate a commit message using OpenAI GPT API.')
    parser.add_argument('--staged', action='store_true', help='Summarize only staged files.')
    parser.add_argument('--api-key', type=str, required=True, help='OpenAI API key.')
    return parser.parse_args()

def main():
    args = parse_args()
    style_guide = read_style_guide()
    files = get_changed_files(staged_only=args.staged)
    diffs = get_file_diffs(files, staged_only=args.staged)
    prompt = construct_prompt(style_guide, files, diffs)
    commit_message = generate_commit_message(prompt, args.api_key)
    print("Generated Commit Message:\n")
    print(commit_message)

if __name__ == '__main__':
    main()
