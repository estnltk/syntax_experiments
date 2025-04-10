import openai
import outlines

from configparser import ConfigParser

def configure_azure_client(config: ConfigParser) -> openai.AzureOpenAI:
    """
    Uses config to set up OpenAI models through Azure interface.
    Returns an openai library client object which is used to interact with OpenAI models.
    Note that client alone is not sufficient to establish a connection.
    One must also specify a deployment name or a model name to start interaction.
    """
    if not config.has_section('azure-configuration'):
        raise ValueError("Configuration does not have section 'azure-configuration'")
    if not config.has_option('azure-configuration', 'api_type'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_type'")
    if not config.has_option('azure-configuration', 'api_key'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_key'")
    if not config.has_option('azure-configuration', 'api_base'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_base'")
    if not config.has_option('azure-configuration', 'api_version'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_version'")
    if not config.has_option('azure-configuration', 'deployment_name'):
        raise ValueError("Section 'azure-configuration' does not have the key 'deployment_name'")
    if not config.has_option('azure-configuration', 'model'):
        raise ValueError("Section 'azure-configuration' does not have the key 'model'")

    return openai.AzureOpenAI(
        azure_endpoint=config['azure-configuration']['api_base'],
        api_key=config['azure-configuration']['api_key'],
        api_version=config['azure-configuration']['api_version']
    )

def configure_outlines_azure_client(config: ConfigParser) -> "outlines.models.openai.OpenAI":
    """
    Uses config to set up OpenAI models through Azure interface.
    Returns a outlies library client object which is used to interact with OpenAI models.
    This model is better than openai library client as one can fix the structure of the output.
    However only new OpenAI models support structured input gpt-4o-xxx, ox, gpt-4.5-xxx.
    """
    if not config.has_section('azure-configuration'):
        raise ValueError("Configuration does not have section 'azure-configuration'")
    if not config.has_option('azure-configuration', 'api_type'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_type'")
    if not config.has_option('azure-configuration', 'api_key'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_key'")
    if not config.has_option('azure-configuration', 'api_base'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_base'")
    if not config.has_option('azure-configuration', 'api_version'):
        raise ValueError("Section 'azure-configuration' does not have the key 'api_version'")
    if not config.has_option('azure-configuration', 'deployment_name'):
        raise ValueError("Section 'azure-configuration' does not have the key 'deployment_name'")
    if not config.has_option('azure-configuration', 'model'):
        raise ValueError("Section 'azure-configuration' does not have the key 'model'")

    return outlines.models.azure_openai(
        deployment_name=config['azure-configuration']['deployment_name'],
        model_name=config['azure-configuration']['model'],
        api_key=config['azure-configuration']['api_key'],
        api_version=config['azure-configuration']['api_version'],
        azure_endpoint=config['azure-configuration']['api_base']
    )
