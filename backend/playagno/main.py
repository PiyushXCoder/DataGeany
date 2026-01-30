# type: ignore

from workflow import ConversationalChartWorkflow
from models import ChatState

workflow = ConversationalChartWorkflow()
state = ChatState()

# ANSI colors
GRAY = "\033[90m"
RESET = "\033[0m"

while True:
    try:
        user_input = input("\nask > ")
        print("\n🤖 > ", end="", flush=True)

        # State is updated in-place by the workflows
        iterator = workflow.run(message=user_input, state=state)
        
        last_type = None
        for event in iterator:
            if event["type"] == "reasoning":
                print(f"\n{GRAY}• {event['content']}{RESET}", end="", flush=True)
            elif event["type"] == "content":
                if last_type == "reasoning":
                    print() # Newline before final answer starts
                print(event["content"], end="", flush=True)
            elif event["type"] == "error":
                print(f"\nError: {event['content']}", end="", flush=True)
            
            last_type = event["type"]
                
        print() # Final newline

    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"\nApp Error: {e}")
