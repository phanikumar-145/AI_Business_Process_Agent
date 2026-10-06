from strands.models.bedrock import BedrockModel


def load_model() -> BedrockModel:
    """Get Amazon Nova 2 Lite through a Bedrock inference profile."""
    return BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0"
    )