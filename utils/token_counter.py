# --- Token Counts (From your variables) ---
# Assuming these variables are populated dynamically during your run
# challenge_agent_billing_inp = 15000 ... etc.

# --- Pricing Constants (Per 1M Tokens) ---

PRICE_GEMINI_25_FLASH_C = 0.075
PRICE_GEMINI_25_FLASH_OUT = 2.50

PRICE_ANTIGRAVITY_IN = 1.50
PRICE_ANTIGRAVITY_C = 0.15
PRICE_ANTIGRAVITY_OUT = 9.00

PRICE_CLAUDE_35_SONNET_IN = 3.00
PRICE_CLAUDE_35_SONNET_C = 0.30
PRICE_CLAUDE_35_SONNET_OUT = 15.00

PRICE_GEMINI_25_LITE_IN = 0.10
PRICE_GEMINI_25_LITE_C = 0.025
PRICE_GEMINI_25_LITE_OUT = 0.40

# --- Cost Calculation ---
def calculate_cost(inp_tokens,out_tokens, price_in, price_out):
    return (inp_tokens / 1_000_000) * price_in + \
           (out_tokens / 1_000_000) * price_out
