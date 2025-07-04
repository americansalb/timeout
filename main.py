import os
import time
from flask import Flask, Response
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ClientTools, AudioInterface

app = Flask(__name__)

# Initialize ElevenLabs client and register the PAUSE tool
api_key = os.environ.get("XI_API_KEY")
xi = ElevenLabs(api_key=api_key)
tools = ClientTools()

def pause_handler(params):
    # Block indefinitely; ElevenLabs will enforce response_timeout_secs
    while True:
        time.sleep(1)

# Register the client tool using its explicit name
tools.register("PAUSE_5_Second", pause_handler)

# Define a dummy audio interface to satisfy abstract methods
class DummyAudioInterface(AudioInterface):
    def start(self):
        pass
    def stop(self):
        pass
    def output(self, data):
        pass
    def interrupt(self):
        pass

# Create a conversation instance so the tool registration takes effect
conversation = Conversation(
    client=xi,
    agent_id=os.environ.get("XI_AGENT_ID"),
    requires_auth=bool(api_key),
    audio_interface=DummyAudioInterface(),
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
