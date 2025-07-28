"""
Generate a psychological profile based on Facebook data using Gemini 2.5 Flash.

This script:
1. Collects all content from data_filtered folder
2. Sends it to Gemini 2.5 Flash via OpenRouter API
3. Uses the prompt from profiler.txt
4. Saves the markdown result to a file
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests
from datetime import datetime
import argparse
import tkinter as tk
from tkinter import messagebox

# Configuration
DATA_DIR = Path("data_filtered")
PROMPT_FILE = Path("prompts/profiler.txt")
OUTPUT_FILE = Path("profile_result.md")

# Default values
DEFAULT_MODEL = "google/gemini-2.5-pro"
DEFAULT_TEMPERATURE = 0.7

# Known context limits (tokens) for some models – extend as needed
MODEL_CONTEXT_LIMITS = {
    "google/gemini-pro": 32768,
    "google/gemini-2.5-flash": 128000,
    "google/gemini-2.5-pro": 1048576,
}

# OpenRouter configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# These will be overwritten from CLI args in main()
MODEL = DEFAULT_MODEL
TEMPERATURE = DEFAULT_TEMPERATURE


def read_file_content(file_path: Path) -> str:
    """Read file content with proper encoding handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""


def collect_data(extensions: Optional[List[str]] = None) -> Tuple[str, int]:
    """
    Collect all content from data_filtered folder.
    
    Returns:
        Tuple containing the concatenated content and total token count estimate
    """
    print("Collecting data from files...")
    all_content = []
    total_chars = 0
    file_count = 0
    
    # Collect files based on provided extensions
    files = []
    ext_patterns = extensions or ["*.md", "*.json"]
    for ext in ext_patterns:
        files.extend(DATA_DIR.rglob(ext))
    
    # Sort files for consistent processing
    files = sorted(files)
    
    # Process each file
    for file_path in files:
        try:
            content = read_file_content(file_path)
            relative_path = file_path.relative_to(DATA_DIR)
            
            # Add file metadata and content
            file_entry = f"\n\n### FILE: {relative_path}\n\n{content}"
            all_content.append(file_entry)
            
            total_chars += len(file_entry)
            file_count += 1
            
            if file_count % 10 == 0:
                print(f"Processed {file_count} files ({total_chars} characters)...")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Join all content
    combined_content = "".join(all_content)
    
    # Estimate tokens (rough estimate: ~4 chars per token)
    estimated_tokens = total_chars // 4
    
    print(f"Collected data from {file_count} files.")
    print(f"Total characters: {total_chars}")
    print(f"Estimated tokens: {estimated_tokens}")
    
    return combined_content, estimated_tokens


def read_prompt() -> str:
    """Read the prompt from profiler.txt."""
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    
    return read_file_content(PROMPT_FILE)


def generate_profile(prompt: str, data: str) -> str:
    """
    Generate psychological profile using Gemini via OpenRouter.
    Continues generation until the profile is complete.
    
    Args:
        prompt: The prompt from profiler.txt
        data: The collected data from all files
    
    Returns:
        The complete generated markdown profile
    """
    print(f"Sending request to {MODEL} via OpenRouter...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Initial prompt with data
    messages = [
        {
            "role": "system",
            "content": "You are a professional psychological profiler analyzing Facebook data exports."
        },
        {
            "role": "user",
            "content": f"{prompt}\n\nHere is the data:\n\n{data}"
        }
    ]
    
    # Initialize variables for the complete profile
    complete_profile = ""
    continuation_attempts = 0
    max_continuation_attempts = 10  # Prevent infinite loops
    
    while continuation_attempts < max_continuation_attempts:
        # Prepare the payload
        if continuation_attempts == 0:
            # First request - use the initial prompt
            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": TEMPERATURE,
                "max_tokens": 4000
            }
        else:
            # Continuation request - ask to continue from where it left off
            continuation_prompt = f"Continue the psychological profile from where you left off. Do not repeat any content already generated. Last part ended with: '{complete_profile[-100:]}'."
            
            # Add the continuation request to messages
            messages.append({"role": "assistant", "content": complete_profile})
            messages.append({"role": "user", "content": continuation_prompt})
            
            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": TEMPERATURE,
                "max_tokens": 4000
            }
        
        try:
            print(f"Generation attempt {continuation_attempts + 1}...")
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                profile_chunk = result["choices"][0]["message"]["content"]
                complete_profile += profile_chunk
                
                # Check if the response is complete
                finish_reason = result["choices"][0].get("finish_reason")
                print(f"Chunk generated: {len(profile_chunk)} chars. Finish reason: {finish_reason}")
                
                if finish_reason == "stop":
                    print("Generation complete!")
                    break
                
                # If we got a substantial chunk but it's not complete, continue
                if len(profile_chunk) < 100:  # Very small response might indicate issues
                    print("Warning: Very small response received. May indicate completion or API issues.")
                    # If the chunk is too small, we might be done or hitting an error
                    if "conclusion" in profile_chunk.lower() or "summary" in profile_chunk.lower():
                        print("Detected conclusion - assuming generation is complete.")
                        break
                
                # Update for next iteration
                continuation_attempts += 1
                
                # Keep only the latest assistant message to avoid token limit issues
                if len(messages) >= 4:  # system, user, assistant, user
                    messages = [
                        messages[0],  # system message
                        messages[1],  # initial user message with data
                        {"role": "assistant", "content": complete_profile}  # combined assistant responses
                    ]
            else:
                raise ValueError(f"Unexpected response format: {result}")
                
        except Exception as e:
            print(f"Error in generation attempt {continuation_attempts + 1}: {e}")
            error_response = ""
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_response = e.response.text
                print(f"Response: {error_response}")
                
                # Check if error is related to context length
                if "context length" in error_response.lower() or "token limit" in error_response.lower() or "too many tokens" in error_response.lower():
                    # Extract token info if available in the error response
                    try:
                        error_json = json.loads(error_response)
                        token_info = ""
                        if "error" in error_json and "message" in error_json["error"]:
                            token_info = error_json["error"]["message"]
                        
                        # Show popup with token information from OpenRouter
                        root = tk.Tk()
                        root.withdraw()  # Hide the main window
                        messagebox.showerror(
                            title="OpenRouter Context Limit Error",
                            message=f"The model {MODEL} context limit was exceeded.\n\n{token_info}"
                        )
                        root.destroy()
                    except json.JSONDecodeError:
                        # Fallback if response isn't valid JSON
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showerror(
                            title="OpenRouter Context Limit Error",
                            message=f"The model {MODEL} context limit was exceeded.\n\nError details: {error_response[:200]}..."
                        )
                        root.destroy()
            
            # If we already have some content, return what we have
            if complete_profile:
                print("Returning partial profile due to error")
                return complete_profile
            raise
    
    return complete_profile


def save_profile(profile_text: str) -> None:
    """Save the generated profile to a markdown file."""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(profile_text)
    
    # Print summary stats
    print(f"Profile saved to {OUTPUT_FILE}")
    print(f"Profile length: {len(profile_text)} characters")
    print(f"Approximate word count: {len(profile_text.split())}")
    
    # Check if profile appears complete
    lower_text = profile_text.lower()
    has_conclusion = any(term in lower_text for term in ["conclusion", "summary", "in summary", "overall"])
    
    if has_conclusion:
        print("Profile appears to be complete (contains conclusion/summary).")
    else:
        print("WARNING: Profile might be incomplete (no conclusion/summary detected).")
        print("Consider running the script again with a continuation prompt.")


def main() -> None:
    """Main function to generate the psychological profile."""
    start_time = time.time()

    # ---------------- CLI argument parsing ----------------
    parser = argparse.ArgumentParser(description="Generate a psychological profile from Facebook data using OpenRouter.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter model identifier to use")
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE, help="Sampling temperature (0-1)")
    parser.add_argument("--extensions", nargs="*", default=["md", "json"], help="File extensions to include, e.g. md json txt")
    args = parser.parse_args()

    global MODEL, TEMPERATURE
    MODEL = args.model
    TEMPERATURE = args.temperature
    extensions = [f"*.{ext.lstrip('.')}" for ext in args.extensions]

    # Read the prompt
    prompt = read_prompt()
    print(f"Prompt loaded ({len(prompt)} characters)")
    
    # Check if we're continuing an existing profile
    continue_existing = False
    existing_profile = ""
    if OUTPUT_FILE.exists():
        user_input = input(f"Existing profile found at {OUTPUT_FILE}. Continue generation? (y/n): ").strip().lower()
        if user_input == 'y':
            continue_existing = True
            existing_profile = read_file_content(OUTPUT_FILE)
            print(f"Loaded existing profile ({len(existing_profile)} characters)")
    
    if continue_existing:
        # For continuation, we'll use a simplified approach
        try:
            # Create a continuation prompt
            continuation_prompt = f"Continue the psychological profile from where you left off. Do not repeat any content already generated. Last part ended with: '{existing_profile[-200:]}'"
            
            # Generate continuation
            continuation = generate_profile(continuation_prompt, "")
            
            # Combine and save
            complete_profile = existing_profile + "\n\n" + continuation
            save_profile(complete_profile)
            
            elapsed_time = time.time() - start_time
            print(f"Profile continuation completed in {elapsed_time:.2f} seconds.")
            
        except Exception as e:
            print(f"Failed to continue profile: {e}")
    else:
        # Generate new profile from scratch
        # Collect data from files
        data, estimated_tokens = collect_data(extensions)
        
        # Check if we're within token limits
        context_limit = MODEL_CONTEXT_LIMITS.get(MODEL)
        if context_limit and estimated_tokens > context_limit:
            error_message = f"WARNING: Estimated tokens ({estimated_tokens}) exceed the context limit ({context_limit}) for model {MODEL}."
            print(error_message)
            
            # Show popup notification
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showwarning(
                title="Context Limit Exceeded",
                message=f"Token limit exceeded for {MODEL}:\n\nEstimated tokens: {estimated_tokens}\nModel limit: {context_limit}\n\nThe request will still be sent, but may fail."
            )
            root.destroy()
        
        # Generate profile
        try:
            profile = generate_profile(prompt, data)
            
            # Save the profile
            save_profile(profile)
            
            elapsed_time = time.time() - start_time
            print(f"Profile generation completed in {elapsed_time:.2f} seconds.")
            
        except Exception as e:
            print(f"Failed to generate profile: {e}")


if __name__ == "__main__":
    main()
