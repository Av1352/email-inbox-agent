"""
Email Inbox Agent Evaluation Environment
Built with hud SDK — demonstrates agent evaluation with live telemetry

Run: python env.py
Watch your trace live at: hud.ai/home
"""

import asyncio
import os
import hud
from hud import Environment
from hud.agents import create_agent
from hud.settings import settings

env = Environment("email-inbox-agent")

# ============================================================
# EMAIL DATASET — realistic inbox with varied scenarios
# ============================================================

EMAILS = [
    {
        "id": "1",
        "from": "cto@company.com",
        "subject": "URGENT: Production database corrupted — all hands",
        "body": "Our primary database has a corruption issue affecting 40% of user records. Engineers are investigating but we need all senior staff on a call NOW. This is a P0 incident.",
        "expected_category": "urgent",
        "expected_priority": "high"
    },
    {
        "id": "2", 
        "from": "newsletter@aiweekly.com",
        "subject": "This week in AI: GPT-5, Gemini updates, and more",
        "body": "Welcome to this week's AI digest. Top stories: OpenAI releases new model...",
        "expected_category": "newsletter",
        "expected_priority": "low"
    },
    {
        "id": "3",
        "from": "sarah.chen@enterprise-client.com", 
        "subject": "Contract renewal — need response by Friday",
        "body": "Hi, our annual contract expires next week. We'd like to renew but need updated pricing. Can we schedule a call? This is time-sensitive for our budget approval.",
        "expected_category": "meeting",
        "expected_priority": "high"
    },
    {
        "id": "4",
        "from": "hr@company.com",
        "subject": "Performance review cycle starting Monday",
        "body": "Reminder: Q1 performance reviews begin Monday. Please complete your self-assessment in Workday by end of week.",
        "expected_category": "work",
        "expected_priority": "medium"
    },
    {
        "id": "5",
        "from": "promo@deals.com",
        "subject": "🔥 Last chance: 70% off everything ends midnight!",
        "body": "MASSIVE SALE! All items 70% off. Use code SAVE70. Shop now before it's too late!!!",
        "expected_category": "promotional",
        "expected_priority": "low"
    },
    {
        "id": "6",
        "from": "alex@team.company.com",
        "subject": "PR review request: authentication refactor",
        "body": "Hey, can you review my PR when you get a chance? It's the auth refactor we discussed — no rush, but would love eyes on it before end of sprint.",
        "expected_category": "work",
        "expected_priority": "medium"
    },
    {
        "id": "7",
        "from": "security@company.com",
        "subject": "Suspicious login attempt detected on your account",
        "body": "We detected a login attempt from an unrecognized device in Moscow, Russia. If this wasn't you, please reset your password immediately.",
        "expected_category": "urgent",
        "expected_priority": "high"
    },
    {
        "id": "8",
        "from": "mom@gmail.com",
        "subject": "Dad's birthday dinner Saturday — are you coming?",
        "body": "Hi honey, just confirming if you'll make it to dad's birthday dinner on Saturday at 7pm. Grandma is coming too!",
        "expected_category": "personal",
        "expected_priority": "medium"
    },
]

# ============================================================
# TOOLS — what the agent can call
# ============================================================

@env.tool()
def list_emails() -> list[dict]:
    """List all emails in the inbox with id, sender, subject."""
    return [
        {"id": e["id"], "from": e["from"], "subject": e["subject"]}
        for e in EMAILS
    ]

@env.tool()
def read_email(email_id: str) -> dict:
    """Read the full content of a specific email by ID."""
    for email in EMAILS:
        if email["id"] == email_id:
            return {k: v for k, v in email.items() 
                    if k not in ["expected_category", "expected_priority"]}
    return {"error": f"Email {email_id} not found"}

@env.tool()
def categorize_email(email_id: str, category: str, priority: str, reason: str) -> dict:
    """
    Categorize an email with category, priority, and reasoning.
    
    Args:
        email_id: The email ID to categorize
        category: One of: urgent, meeting, newsletter, personal, promotional, work
        priority: One of: high, medium, low  
        reason: Brief explanation for the categorization
    """
    valid_categories = ["urgent", "meeting", "newsletter", "personal", "promotional", "work"]
    valid_priorities = ["high", "medium", "low"]
    
    if category not in valid_categories:
        return {"error": f"Invalid category '{category}'. Must be one of: {valid_categories}"}
    if priority not in valid_priorities:
        return {"error": f"Invalid priority '{priority}'. Must be one of: {valid_priorities}"}
    
    return {
        "success": True,
        "email_id": email_id,
        "category": category,
        "priority": priority,
        "reason": reason
    }

@env.tool()
def get_urgent_emails() -> list[dict]:
    """Get a summary of all emails marked as urgent that need immediate attention."""
    return [
        {"id": e["id"], "from": e["from"], "subject": e["subject"]}
        for e in EMAILS
        if e["expected_priority"] == "high"
    ]

# ============================================================
# SCENARIOS — how the agent is evaluated
# ============================================================

@env.scenario("triage-inbox")
async def triage_inbox():
    """
    Full inbox triage — agent must categorize all emails correctly.
    Score = (correct categories + correct priorities) / (total * 2)
    """
    result = yield (
        "You are an email assistant. Triage the entire inbox:\n"
        "1. List all emails\n"
        "2. Read each email carefully\n"
        "3. Categorize each with: category (urgent/meeting/newsletter/personal/promotional/work) and priority (high/medium/low)\n"
        "4. Use the categorize_email tool for each one\n"
        "Start now."
    )
    
    # Score based on result content matching expected values
    correct_categories = 0
    correct_priorities = 0
    
    for email in EMAILS:
        result_str = str(result).lower()
        if email["expected_category"] in result_str and email["id"] in result_str:
            correct_categories += 1
        if email["expected_priority"] in result_str and email["id"] in result_str:
            correct_priorities += 1
    
    total = len(EMAILS)
    score = (correct_categories + correct_priorities) / (total * 2)
    yield score


@env.scenario("identify-urgent")
async def identify_urgent():
    """
    Agent must identify all high-priority emails that need immediate attention.
    Score = recall of urgent emails identified.
    """
    result = yield (
        "Review the inbox and identify ALL emails requiring immediate attention. "
        "List the email IDs and subjects of anything urgent or time-sensitive."
    )
    
    urgent_ids = ["1", "3", "7"]  # P0 incident, contract deadline, security alert
    found = sum(1 for uid in urgent_ids if uid in str(result))
    yield found / len(urgent_ids)


@env.scenario("spam-filter")
async def spam_filter():
    """
    Agent must correctly identify promotional/spam emails.
    Score = precision + recall of spam identification.
    """
    result = yield (
        "Which emails in this inbox are promotional, spam, or can be safely ignored? "
        "List their IDs."
    )
    
    spam_ids = ["2", "5"]  # newsletter, promo
    found = sum(1 for sid in spam_ids if sid in str(result))
    # Penalty for false positives (marking important emails as spam)
    important_ids = ["1", "3", "7"]
    false_positives = sum(1 for iid in important_ids if iid in str(result))
    
    score = max(0, (found / len(spam_ids)) - (false_positives * 0.3))
    yield score


# ============================================================
# MAIN — run agent against all scenarios with live telemetry
# ============================================================

async def main():
    print("\n" + "="*60)
    print("📧 EMAIL INBOX AGENT EVALUATION")
    print("Powered by hud — watch live at hud.ai/home")
    print("="*60 + "\n")
    
    scenarios = [
        ("triage-inbox", "Full Inbox Triage"),
        ("identify-urgent", "Urgent Email Detection"), 
        ("spam-filter", "Spam Filtering"),
    ]
    
    results = {}
    
    for scenario_id, scenario_name in scenarios:
        print(f"🚀 Running: {scenario_name}")
        print(f"   Scenario: {scenario_id}")
        
        task = env(scenario_id)
        agent = create_agent("claude-sonnet-4-5")
        
        async with hud.eval(task) as ctx:
            result = await agent.run(ctx, max_steps=15)
        
        results[scenario_name] = result.reward
        print(f"   ✅ Score: {result.reward:.2f}/1.0\n")
    
    print("="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    for name, score in results.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"{name:<30} [{bar}] {score:.2f}")
    
    avg = sum(results.values()) / len(results)
    print(f"\n{'Average Score':<30} {avg:.2f}/1.0")
    print("\n🔍 View full traces at: hud.ai/home")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())