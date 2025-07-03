from typing import Dict
from typing import List

def SystemPrompt(text: str) -> Dict[str, str]:
    """Properly encapsulated system prompt."""
    return {'role': 'system', 'content': text}

def UserPrompt(text:str) -> Dict[str, str]:
    """Properly encapsulated user prompt."""
    return {'role': 'user', 'content': text}

def AssistantPrompt(text: str) -> Dict[str, str]:
    """Properly encapsulated assistant prompt."""
    return {'role': 'assistant', 'content': text}

def InputList(entries: List[str], format: str = "line_separated") -> str:
    """
    Places entries into text prompt according to specified format:

    - coma_separated:
      Entries are separated by a coma character.

    - line_separated:
      Entries are separated by a newline character.

    - numbered_and_quoted_list:
      Each entry is numbered and quoted and separated by a newline character.
    """

    if format == "line_separated":
        return "\n".join(entries)
    elif format == "numbered_and_quoted_list":
        return "\n".join(f'{i+1}. "{x}"' for i, x in enumerate(entries))
    elif format == "coma_separated":
        return "\n".join(entries)
    else:
        raise NotImplementedError(f'Format "{format}" is not a vlid choice')
