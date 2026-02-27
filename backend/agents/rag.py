import os


def load_knowledge():

    base_path = os.path.join(
        os.path.dirname(__file__),
        "knowledge"
    )

    knowledge = {}

    for filename in os.listdir(base_path):
        if filename.endswith(".txt"):
            with open(os.path.join(base_path, filename), "r") as f:
                knowledge[filename] = f.read()

    return knowledge


def retrieve_relevant_knowledge(state):

    knowledge = load_knowledge()

    retrieved = {}

    # Simple rules (replace with embeddings later)
    if state.flood_event["severity"] >= 4:
        retrieved["flood_sop"] = knowledge.get("flood_sop.txt")

    if state.medical_flags:
        retrieved["medical_sop"] = knowledge.get("medical_sop.txt")

    if sum(state.clusters.values()) > 100:
        retrieved["shelter_sop"] = knowledge.get("shelter_sop.txt")

    return retrieved