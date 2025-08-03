

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner, set_tracing_disabled,
from agents import RunContextWrapper, function_tool
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import asyncio
from openai.types.responses import ResponseTextDeltaEvent




#📦 Load environment variables
load_dotenv()
set_tracing_disabled(disabled=True)

# 🔐 Load API Key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 🤖 Setup Gemini Model
ex_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=ex_client
)

# 🧾 User Context Model
class UserContext(BaseModel):
    name: str
    account_number: str
    is_premium_user: bool
    issue_type: str  # billing / technical / general

# 💳 Billing Tool (Only for Premium Users)
@function_tool(is_enabled=lambda ctx, _: ctx.context.is_premium_user)
async def process_refund(ctx: RunContextWrapper[UserContext]) -> str:
    return f"✅ Refund has been initiated for account {ctx.context.account_number}, {ctx.context.name}. You'll be notified once processed."

# ⚙️ Technical Tool (Only for Technical Issues)
@function_tool(is_enabled=lambda ctx, _: ctx.context.issue_type == "technical")
async def restart_service(ctx: RunContextWrapper[UserContext]) -> str:
    return f"🔄 Online banking service for account {ctx.context.account_number} has been restarted. Try logging in again, {ctx.context.name}."

# 💼 Billing Agent
billing_agent = Agent(
    name="billing agent",
    instructions="""
You are a helpful bank billing assistant. Always respond in polite, professional Urdu.

You handle:
1. Duplicate transactions → Ask user for transaction ID or date.
2. Monthly fee disputes → Ask for account number and the date of the fee.
3. Refund requests → Ask for date, amount, and type of transaction (e.g., ATM withdrawal, online shopping).
4. Statement requests → Ask for the time period (e.g., last 1 month or specific dates).

If user says "last transaction ka refund chahiye", politely say:
"Meherbani farma kar, apni aakhri transaction ki tareekh, raqam aur kis qisam ki transaction thi woh bataiye — taake hum aapki madad kar saken."
""",

   
    tools=[process_refund],
   
    model=model
)

# 🛠 Technical Agent
technical_agent = Agent(
    name="technical support agent",
    instructions="""
You are a bank's technical support assistant. Help users with:
- Mobile/online banking problems
- OTP not working
- Login errors or system crashes
""",
    tools=[restart_service],
    model=model
)

# 💬 General Agent
general_agent = Agent(
    name="general support agent",
    instructions="""
You are a general banking assistant. Help users with common questions like:
- Interest rates
- Branch timings
- Account types and services
""",
    model=model
)

# 🔀 Triage Agent
triage_agent = Agent(
    name="triage agent",
    instructions="""
You are a smart routing assistant for bank customer queries.

- If the issue is billing-related, forward to the billing agent.
- If technical, forward to technical support.
- Otherwise, handle via general support.
""",


    model=model,
    handoffs=[billing_agent, technical_agent, general_agent]
)

# ⚙️ Configuration
config = RunConfig(
    model=model,
    model_provider=ex_client,
)

# 🧠 Main function
async def main():
    # 🧑‍💻 User Input
    name = input("👤 Enter your full name: ")
    account_number = input("🏦 Enter your account number: ")
    is_premium = input("💎 Are you a premium user? (yes/no): ").strip().lower() == "yes"
    issue_type = input("❓ What is your issue type? (billing/technical/general): ").strip().lower()
    user_query = input("💬 Describe your issue: ")

    # 🧠 Run Agent
    context = UserContext(
        name=name,
        account_number=account_number,
        is_premium_user=is_premium,
        issue_type=issue_type
    )

    result = Runner.run_streamed(
        triage_agent,
        user_query,
        context=context,
        run_config=config
    )

    print("\n📨 Bank Support Response:")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

    print("\n\n✅ Final Output:")
    print(result.final_output)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
