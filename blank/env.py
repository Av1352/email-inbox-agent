from hud.environment import Environment

env = Environment("email-inbox-agent")

# Sample email dataset
EMAILS = [
    {
        "id": "1",
        "from": "boss@company.com",
        "subject": "URGENT: Server down in production",
        "body": "The main server is down. Customers can't access the platform. Need immediate action.",
        "timestamp": "2024-01-15 09:00"
    },
    {
        "id": "2",
        "from": "newsletter@medium.com",
        "subject": "Top 10 AI articles this week",
        "body": "Here are the top articles in AI this week...",
        "timestamp": "2024-01-15 08:30"
    },
    {
        "id": "3",
        "from": "client@bigcorp.com",
        "subject": "Meeting tomorrow at 2pm?",
        "body": "Hi, are you available for a quick sync tomorrow at 2pm to discuss the project status?",
        "timestamp": "2024-01-15 08:00"
    },
    {
        "id": "4",
        "from": "hr@company.com",
        "subject": "Benefits enrollment deadline Friday",
        "body": "Reminder: Benefits enrollment closes this Friday. Please complete your selection.",
        "timestamp": "2024-01-14 17:00"
    },
    {
        "id": "5",
        "from": "no-reply@amazon.com",
        "subject": "Your order has shipped",
        "body": "Your order #12345 has shipped and will arrive by Thursday.",
        "timestamp": "2024-01-14 15:00"
    },
    {
        "id": "6",
        "from": "colleague@company.com",
        "subject": "Quick question about the report",
        "body": "Hey, can you clarify what methodology you used in section 3 of the Q4 report?",
        "timestamp": "2024-01-14 14:00"
    },
    {
        "id": "7",
        "from": "promo@shop.com",
        "subject": "50% OFF everything today only!",
        "body": "HUGE SALE! Don't miss out on 50% off all items. Limited time offer!",
        "timestamp": "2024-01-14 10:00"
    },
    {
        "id": "8",
        "from": "doctor@clinic.com",
        "subject": "Appointment reminder: Tomorrow 10am",
        "body": "This is a reminder for your appointment tomorrow at 10am. Please arrive 10 minutes early.",
        "timestamp": "2024-01-14 09:00"
    }
]

# Tools the agent can use
@env.tool()
def list_emails() -> list[dict]:
    """List all emails in the inbox with id, from, subject, and timestamp."""
    return [{"id": e["id"], "from": e["from"], "subject": e["subject"], "timestamp": e["timestamp"]} for e in EMAILS]

@env.tool()
def read_email(email_id: str) -> dict:
    """Read the full content of an email by its ID."""
    for email in EMAILS:
        if email["id"] == email_id:
            return email
    return {"error": f"Email {email_id} not found"}

@env.tool()
def categorize_email(email_id: str, category: str, priority: str) -> dict:
    """
    Categorize an email.
    
    Args:
        email_id: The email ID to categorize
        category: One of: urgent, meeting, newsletter, personal, promotional, work
        priority: One of: high, medium, low
    
    Returns:
        Confirmation of categorization
    """
    valid_categories = ["urgent", "meeting", "newsletter", "personal", "promotional", "work"]
    valid_priorities = ["high", "medium", "low"]
    
    if category not in valid_categories:
        return {"error": f"Invalid category. Must be one of: {valid_categories}"}
    if priority not in valid_priorities:
        return {"error": f"Invalid priority. Must be one of: {valid_priorities}"}
    
    return {
        "success": True,
        "email_id": email_id,
        "category": category,
        "priority": priority
    }

@env.tool()
def get_summary() -> dict:
    """Get a summary of all categorizations made so far."""
    return {"message": "Summary requested - agent should provide categorization results"}


# Evaluation scenarios
@env.scenario("categorize-urgent")
async def categorize_urgent():
    """Test if agent correctly identifies and prioritizes urgent emails."""
    result = yield "Please categorize all emails in the inbox. Focus on correctly identifying urgent items that need immediate attention."
    
    # Score based on whether the production server email was marked urgent/high
    if "1" in str(result) and ("urgent" in str(result).lower() or "high" in str(result).lower()):
        yield 1.0
    else:
        yield 0.0

@env.scenario("filter-spam")
async def filter_spam():
    """Test if agent correctly identifies promotional/spam emails."""
    result = yield "Review the inbox and identify which emails are promotional or spam that can be safely ignored."
    
    # Score based on whether promo emails (ids 2, 5, 7) are identified
    promo_found = sum(1 for id in ["2", "5", "7"] if id in str(result))
    yield promo_found / 3.0

@env.scenario("prioritize-responses")
async def prioritize_responses():
    """Test if agent correctly identifies emails that need a reply."""
    result = yield "Which emails require a response from me, and in what order should I respond to them?"
    
    # Emails needing response: 1 (urgent), 3 (meeting request), 6 (colleague question), 8 (appointment)
    response_emails = sum(1 for id in ["1", "3", "6"] if id in str(result))
    yield response_emails / 3.0


if __name__ == "__main__":
    import asyncio
    from hud.scenario import run_scenario
    
    async def main():
        print("Running email inbox agent evaluation...")
        
        # Run all scenarios
        scenarios = ["categorize-urgent", "filter-spam", "prioritize-responses"]
        results = {}
        
        for scenario in scenarios:
            print(f"\nRunning scenario: {scenario}")
            score = await run_scenario(env, scenario)
            results[scenario] = score
            print(f"Score: {score:.2f}")
        
        print("\n--- Final Results ---")
        for scenario, score in results.items():
            print(f"{scenario}: {score:.2f}")
        avg = sum(results.values()) / len(results)
        print(f"Average score: {avg:.2f}")
    
    asyncio.run(main())