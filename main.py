import os
import time
from flask import Flask, Response, request, abort
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ClientTools, AudioInterface

app = Flask(__name__)

# ---------------------------------------------------------------------------
#  Build a flexible agent map
# ---------------------------------------------------------------------------
# Every environment variable that starts with "AGENT_" is treated as
# an agent entry. Example in Render:
#   AGENT_PAUSE_ID     = agent_01jz3mzxkkfw09832nvhjtqxvy
#   AGENT_NG_GRAMMAR_ID = agent_01jz3qjsftfrt8jhzg64bmfdrz
# You can add AGENT_SOMETHING_ELSE_ID later and it will be picked up
# automatically on the next deploy.

AGENT_PREFIX = "AGENT_"
AGENTS = {
    var[len(AGENT_PREFIX):].lower(): value  # e.g. "pause": "agent_01jz..."
    for var, value in os.environ.items()
    if var.startswith(AGENT_PREFIX) and value
}
if not AGENTS:
    raise RuntimeError("No agent IDs found. Add env vars like AGENT_MY_AGENT_ID=<id>.")

# ---------------------------------------------------------------------------
#  ElevenLabs client & tool registration
# ---------------------------------------------------------------------------

api_key = os.environ.get("XI_API_KEY")
if not api_key:
    raise RuntimeError("XI_API_KEY is not set")

xi = ElevenLabs(api_key=api_key)

tools = ClientTools()

# Dummy audio interface to satisfy abstract base class
class DummyAudioInterface(AudioInterface):
    def start(self):
        pass
    def stop(self):
        pass
    def output(self, data):
        pass
    def interrupt(self):
        pass

def pause_handler(params):
    """Block for ten seconds (ElevenLabs enforces time‑out)."""
    time.sleep(10)

# Register the client tool once
TOOLS_NAME = os.environ.get("TOOL_NAME", "PAUSE_5_Second")

tools.register(TOOLS_NAME, pause_handler)

# Attach the tool to every agent so each one can invoke it.
for _tag, _agent_id in AGENTS.items():
    Conversation(
        client=xi,
        agent_id=_agent_id,
        requires_auth=bool(api_key),
        audio_interface=DummyAudioInterface(),
        client_tools=tools,
    )

# ---------------------------------------------------------------------------
#  Routes
# ---------------------------------------------------------------------------

@app.route("/pause", methods=["POST"])
def pause():
    """Called by ElevenLabs when the PAUSE tool is invoked."""
    pause_handler(None)
    return Response(status=204)

@app.route("/agents", methods=["GET"])
def list_agents():
    """Quick sanity check: returns the available agent tags."""
    return {"available_agents": list(AGENTS.keys())}

@app.route("/ping/<agent_tag>", methods=["GET"])
def ping(agent_tag: str):
    """Very light health check per agent tag."""
    if agent_tag not in AGENTS:
        abort(404, "Unknown agent tag")
    return {"agent_id": AGENTS[agent_tag]}

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
