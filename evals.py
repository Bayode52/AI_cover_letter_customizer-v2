from groq import Groq

# Replace with your API key or load from environment variable
API_KEY = "your_groq_api_key"

# --- TEST CASES ---
test_cases = [
    {
        "job": "Software Engineer role requiring Python, cloud experience, and teamwork.",
        "background": "3 years as a Python developer. Built REST APIs. Used AWS. Led a small team on a migration project.",
        "checks": [
            "Mentions Python",
            "Mentions cloud or AWS",
            "Mentions teamwork or team",
            "Starts with 'Dear Hiring Manager'",
            "Ends with 'Sincerely'",
            "Under 400 words"
        ]
    },
    {
        "job": "Marketing Manager role requiring campaign experience, analytics, and leadership.",
        "background": "5 years in digital marketing. Ran email campaigns. Used Google Analytics. Managed 2 junior marketers.",
        "checks": [
            "Mentions campaign or campaigns",
            "Mentions analytics or data",
            "Mentions leadership or managed or lead or led or manage",
            "Starts with 'Dear Hiring Manager'",
            "Ends with 'Sincerely'",
            "Under 400 words"
        ]
    },
    {
        "job": "Customer Support role requiring communication skills, patience, and CRM experience.",
        "background": "Worked retail for 2 years. Handled customer complaints. No CRM experience yet. Good communicator.",
        "checks": [
            "Mentions communication or communicator",
            "Mentions customer or customers",
            "Does NOT invent CRM experience",
            "Starts with 'Dear Hiring Manager'",
            "Ends with 'Sincerely'",
            "Under 400 words"
        ]
    }
]

# --- THE PIPELINE (same as your Streamlit app, but as a function) ---

def generate_cover_letter(job_description, background):
    """Runs the two-step AI pipeline and returns: first_draft, feedback, final_letter"""
    client = Groq(api_key=API_KEY)

    # Step 1: Draft
    draft_prompt = f"""
You are a professional cover letter writer.

Write a tailored cover letter based on the job description and the candidate's background.
Rules:
- Keep it under 300 words.
- Professional but warm tone.
- Highlight relevant skills.
- Do not invent experience.
- Start with "Dear Hiring Manager," and end with "Sincerely,".

Job Description:
{job_description}

Candidate Background:
{background}

Cover Letter:
"""
    draft_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful career assistant."},
            {"role": "user", "content": draft_prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )
    first_draft = draft_response.choices[0].message.content

    # Step 2: Review
    review_prompt = f"""
You are a strict but constructive cover letter editor.

Review the cover letter below against the job description. Then produce an improved version.

Step 1: List 2-3 specific things that could be improved.
Step 2: Write the improved cover letter.

Format:
FEEDBACK:
- [Point 1]
- [Point 2]

IMPROVED COVER LETTER:
[The full improved cover letter]

Job Description:
{job_description}

Original Cover Letter:
{first_draft}
"""
    review_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a meticulous editor."},
            {"role": "user", "content": review_prompt}
        ],
        temperature=0.5,
        max_tokens=1024
    )
    review_output = review_response.choices[0].message.content

    # Parse
    if "IMPROVED COVER LETTER:" in review_output:
        parts = review_output.split("IMPROVED COVER LETTER:", 1)
        feedback = parts[0].replace("FEEDBACK:", "").strip()
        final_letter = parts[1].strip()
    else:
        feedback = "Could not parse feedback."
        final_letter = review_output

        # DEBUG: Print what the final letter actually looks like
    print(f"\nDEBUG Final Letter repr (first 100 chars): {repr(final_letter[:100])}")
    print(f"DEBUG Final Letter word count: {len(final_letter.split())}")
    print(f"DEBUG Final Letter last 50 chars: {repr(final_letter[-50:])}")

    return first_draft, feedback, final_letter


# --- EVALUATION LOGIC ---
def evaluate(final_letter, checks):
    """Runs each check against the final letter. Returns score and details."""
    clean_letter = final_letter.strip()
    
    results = []
    for check in checks:
        if check.startswith("Does NOT"):
            phrase = check.replace("Does NOT ", "")
            passed = phrase.lower() not in clean_letter.lower()
        elif check.startswith("Under "):
            word_count = len(clean_letter.split())
            max_words = int(check.replace("Under ", "").replace(" words", ""))
            passed = word_count <= max_words
        elif check.startswith("Starts with"):
            phrase = check.replace("Starts with ", "").strip().strip("'").strip('"')
            passed = clean_letter.lower().startswith(phrase.lower())
        elif check.startswith("Ends with"):
            phrase = check.replace("Ends with ", "").strip().strip("'").strip('"')
            # Check if the letter CONTAINS the phrase near the end, not ends exactly with it
            # Take last 100 characters and check if phrase is in there
            last_chunk = clean_letter.lower()[-100:]
            passed = phrase.lower() in last_chunk
       
        elif check.startswith("Mentions "):
            # Extract the keyword(s) after "Mentions "
            keywords = check.replace("Mentions ", "")
            # Handle "or" logic: "Python or programming" means either word passes
            options = [k.strip().lower() for k in keywords.split(" or ")]
            passed = any(option in clean_letter.lower() for option in options)
        else:
            passed = check.lower() in clean_letter.lower()

        results.append({"check": check, "passed": passed})

    score = sum(1 for r in results if r["passed"])
    return score, len(checks), results


# --- RUN EVALS ---

print("=" * 50)
print("COVER LETTER EVALUATION REPORT")
print("=" * 50)

total_score = 0
total_checks = 0

for i, case in enumerate(test_cases, 1):
    print(f"\n--- Test Case {i} ---")
    print(f"Job: {case['job'][:60]}...")
    print(f"Background: {case['background'][:60]}...")

    first_draft, feedback, final_letter = generate_cover_letter(case["job"], case["background"])
    score, max_score, results = evaluate(final_letter, case["checks"])

    total_score += score
    total_checks += max_score

    print(f"Score: {score}/{max_score}")
    for r in results:
        symbol = "PASS" if r["passed"] else "FAIL"
        print(f"  [{symbol}] {r['check']}")

    # Show the failing checks with context
    if score < max_score:
        print(f"\n  Final Letter Preview: {final_letter[:200]}...")

print("\n" + "=" * 50)
print(f"OVERALL SCORE: {total_score}/{total_checks} ({total_score/total_checks*100:.1f}%)")
print("=" * 50)
