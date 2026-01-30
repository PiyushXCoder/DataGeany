from dotenv import load_dotenv
load_dotenv()

import os

from workflow import ConversationalChartWorkflow
from models import ChatState

workflow = ConversationalChartWorkflow()
state = ChatState()

while True:
    user_input = input("\n🧑 > ")

    response, state = workflow.run(
        message=user_input,
        state=state
    )

    print("\n🤖 >", response)
