# Add other bot managers here
from . import openai_manager
from . import claude_manager


# GENERAL TRIAGE
def triage_response_from_bot(bot_name: str, model_name: str, prompt: str) -> str:
    if bot_name == "openai":
        bot_resp = triage_response_from_openai_models(model_name, prompt)
        return bot_resp
    elif bot_name == "claude":
        bot_resp = triage_response_from_claude_models(model_name, prompt)
        return bot_resp
    else:
        raise RuntimeError(f"ERROR: Attempted to triage {bot_name}, but its triage hasn't been implemented yet in"
                           f"chat_model_triage_manager.py under the triage_response_from_bot function.")


# OPENAI MODELS
def triage_response_from_openai_models(model_name: str, prompt: str) -> str:
    model_client = openai_manager.setup()
    model_response = openai_manager.prompt_openai(model_client, model_name, prompt)
    return model_response


# CLAUDE MODELS
def triage_response_from_claude_models(model_name: str, prompt: str) -> str:
    model_client = claude_manager.setup()
    model_response = claude_manager.prompt_claude(model_client, model_name, prompt)
    return model_response

