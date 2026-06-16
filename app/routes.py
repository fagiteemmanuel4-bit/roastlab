import os
import json
import re
from flask import Blueprint, render_template, request, send_from_directory
import requests

bp = Blueprint('routes', __name__)

def extract_valid_json(raw_response):
    """
    Cleans raw AI response text of markdown wrappers (```json ... ```) 
    and handles common decoding snags cleanly.
    """
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)

@bp.route('/', methods=['GET', 'POST'])
def index():
    roast_result = None
    user_input = ""
    selected_intensity = "Savage"
    selected_personality = "Tech Bro"

    if request.method == 'POST':
        user_input = request.form.get('user_input', '')
        selected_intensity = request.form.get('intensity', 'Savage')
        selected_personality = request.form.get('personality', 'Tech Bro')
        is_pro = request.form.get('is_pro', 'false') == 'true'

        if user_input.strip():
            # Core Thinking Logic 4-Phase System Prompt
            phases_instruction = (
                "PROCESS FLOW: You must process the input through these four strict sequential phases:\n"
                "1. COMPONENT DISSECTION: Break down feasibility, capital modeling, and mechanics.\n"
                "2. ADVERSARIAL ATTACK (THE ROAST): Identify structural points of failure (poor unit economics, regulatory walls).\n"
                "3. THE RECONSTRUCTION (THE PIVOT): Provide immediate, high-yield actionable alternative strategies for every flaw found.\n"
                "4. METRIC MAPPER: Calculate explicit percentage scores for Market Readiness, Capital Efficiency, and Execution."
            )

            system_prompt = (
                "You are a master roast AI in a premium brutalist editorial startup review system (KRYONARA LABS CORE).\n"
                f"Persona: '{selected_personality}'. Intensity: '{selected_intensity}'.\n"
                f"{phases_instruction}\n\n"
                "You must evaluate the user's input and reply ONLY with a raw valid JSON object.\n"
                "The response must be pure JSON containing these exact keys:\n"
                "1. 'headline': Short, devastating editorial hook quotes summarizing the project flaws.\n"
                "2. 'score': An integer rating out of 100 based on execution quality.\n"
                "3. 'roast_bullets': An array containing exactly 5 quick, sharp, witty punchlines mapping critical flaws (Phase 2).\n"
                "4. 'brutal_truth': A paragraph detailing why the market segment or mechanics won't survive long term (Phase 2).\n"
                "5. 'reconstruction': A detailed strategic pivot and actionable alternative strategies (Phase 3).\n"
                "6. 'metrics': An object with 'market_readiness', 'capital_efficiency', and 'execution' percentage scores (Phase 4).\n"
                "7. 'dissection': A breakdown of feasibility and mechanics (Phase 1)."
            )

            if not is_pro:
                # Standard Gate: block processing after Phase 2
                roast_result = {
                    "headline": "SUBSCRIPTION ACCESS RESTRICTED",
                    "score": 0,
                    "roast_bullets": ["BLOCK: PHASE 3 & 4 REDACTED"],
                    "brutal_truth": "[ERROR: VECTOR MAP BLOCK. SUBSCRIPTION UPGRADE REQUIRED TO ACCESS THE PIVOT ENGINE & RECONSTRUCTION LAYER.]",
                    "reconstruction": "LOCKED",
                    "metrics": {"market_readiness": 0, "capital_efficiency": 0, "execution": 0},
                    "dissection": "COMPLETED"
                }
                return render_template(
                    'index.html',
                    roast_result=roast_result,
                    user_input=user_input,
                    selected_intensity=selected_intensity,
                    selected_personality=selected_personality
                )

            api_key = os.getenv("OPENROUTER_API_KEY")

            if api_key:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://127.0.0.1:5000", 
                    "X-Title": "RoastLab AI"
                }
                payload = {
                    "model": "openrouter/free", 
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                }

                try:
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions", 
                        json=payload, 
                        headers=headers,
                        timeout=30
                    )
                    if response.status_code == 200:
                        raw_content = response.json()['choices'][0]['message']['content']
                        roast_result = extract_valid_json(raw_content)
                    else:
                        roast_result = {
                            "headline": "Server Exhaustion Fault", 
                            "score": 0, 
                            "roast_bullets": [f"API returned status code: {response.status_code}"], 
                            "brutal_truth": "OpenRouter free pool is currently overloaded. Please retry in a few seconds.", 
                            "reconstruction": "Your concept is fine, the server network routing is the issue here.",
                            "metrics": {"market_readiness": 0, "capital_efficiency": 0, "execution": 0},
                            "dissection": "System limits."
                        }
                except Exception as e:
                    roast_result = {
                        "headline": "Connection Fault", 
                        "score": 0, 
                        "roast_bullets": [str(e)], 
                        "brutal_truth": "Failed to sync with OpenRouter servers.", 
                        "reconstruction": "None.",
                        "metrics": {"market_readiness": 0, "capital_efficiency": 0, "execution": 0},
                        "dissection": "Connection timeouts."
                    }
            else:
                roast_result = {
                    "headline": "Substack for ADHD-addled attention spans",
                    "score": 15,
                    "roast_bullets": [
                        "Seven seconds? That's barely enough time to clear your throat.",
                        "So, just a series of rapid-fire audible shrugs?",
                        "Perfect for people who want less content, but somehow more annoying.",
                        "Is 'ums' and 'uhs' the new content goto?",
                        "Finally, a podcast for your housefly!"
                    ],
                    "brutal_truth": "You're trying to inject a format constraint (7 seconds) into a platform (Substack) built for depth, analysis, and narrative. Content creators generally want more space, not less, to convey value.",
                    "reconstruction": "Pivot from '7 seconds' to short-form narrative audio channels (1-3 minutes) focused on concise storytelling instead of simple soundbites.",
                    "metrics": {"market_readiness": 20, "capital_efficiency": 40, "execution": 15},
                    "dissection": "Audio content platform with artificial constraints on duration."
                }

    return render_template(
        'index.html', 
        roast_result=roast_result, 
        user_input=user_input,
        selected_intensity=selected_intensity,
        selected_personality=selected_personality
    )

@bp.route('/favicon.ico')
def favicon():
    # Quiet the 404 errors on direct favicon requests from browsers
    return send_from_directory(os.path.join(bp.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Support direct template renderings
@bp.route('/privacy.html')
@bp.route('/compliance/privacy')
def privacy():
    return render_template('privacy.html')

@bp.route('/terms.html')
@bp.route('/compliance/terms')
def terms():
    return render_template('terms.html')

@bp.route('/DCL.html')
@bp.route('/compliance/cryptography')
def cryptography():
    return render_template('DCL.html')

@bp.route('/Model.html')
@bp.route('/compliance/parameters')
def parameters():
    return render_template('Model.html')

@bp.route('/company/manifesto')
@bp.route('/manifesto.html')
def manifesto():
    return render_template('manifesto.html')

@bp.route('/company/pricing')
@bp.route('/enterprise.html')
def pricing():
    return render_template('enterprise.html')

@bp.route('/company/protocol')
@bp.route('/TAP.html')
def protocol():
    return render_template('TAP.html')

@bp.route('/company/logs')
@bp.route('/engin_log.html')
def logs():
    return render_template('engin_log.html')

@bp.route('/compliance/eu-ai')
@bp.route('/eu_ai.html')
def eu_ai():
    return render_template('eu_ai.html')
