# Token Counter
FREE_TIER_LIMIT = 4_000_000

def count_tokens(YOUR_DAILY_LIMIT: int, response: object): 
    """# 1. Fetch your running total from your own database/file
    current_total_used = get_saved_token_count() 
    used_in_this_call = response.usage_metadata.total_token_count

    # 3. Update your running total
    new_total = current_total_used + used_in_this_call
    save_token_count(new_total)

    # 4. Calculate your percentage
    percentage_used = (new_total / YOUR_DAILY_LIMIT) * 100
    print(f"You have used {percentage_used:.2f}% of your daily tokens.")"""
