import os
import time
from flask import Flask, Response, request
from elevenlabs import ElevenLabsClient, ClientTools

app = Flask(__name__)

# Initialize ElevenLabs client and register the PAUSE tool
xi = ElevenLabsClient(api_key=os.environ.get("XI_API_KEY"))
tools = ClientTools()

def pause_handler(params):
    # Block indefinitely; ElevenLabs will enforce response_timeout_secs
    while True:
        time.sleep(1)

# Register the client tool with the exact name from the dashboard
tools.register(os.environ.get("TOOL_NAME"), pause_handler)

# Create a conversation instance so the tool registration takes effect
conversation = xi.conversation(
    agent_id=os.environ.get("XI_AGENT_ID"),
    client_tools=tools
)

@app.route("/pause", methods=["POST"])
def pause():
    # Called by ElevenLabs when PAUSE_5_Second is invoked
    pause_handler(None)
    return Response(status=204)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
