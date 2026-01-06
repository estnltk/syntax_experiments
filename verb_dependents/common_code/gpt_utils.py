import json 



def in2json(sisend):
    """Input dict/json to string using json.dumps.
    """
    return json.dumps(sisend, ensure_ascii=False)


def user_message(lause, fraas):
    """Creates user message with role:user and content is input sentence and phrase.
    """
    mes ={
            "role": "user",
            "content": {"l": lause, "c": fraas}
            }
    return mes


def assistant_message(yesno, short_ans, long_ans):
    """Creates assistant message with role:assistant and content is yes/no, short answer and long answer.
    """
    mes = {
            "role": "assistant",
            "content": {"a": yesno, "s": short_ans, "r": long_ans}
            }
    return mes


def messages_2_str(messages:list[dict]):
    """Creates few-shot examples as one string. Makes 5-row blocks of sentence, phrase, yes/no answer, short answer, long answer.
    """
    # kui tahta samad dict prompti asjad anda ette lihtsalt stringina
    # tekitab 5-realised blokid, eraldatud: \n\n
    
    new_string = ""
    
    for mes in messages:
        if mes["role"]=="user":
            l = mes["content"]["l"]
            c = mes["content"]["c"]
            new_string += f"l: {l}\n"
            new_string += f"c: {c}\n"
        if mes["role"]=="assistant":
            a = mes["content"]["a"]
            s = mes["content"]["s"]
            r = mes["content"]["r"]
            new_string += f"a: {a}\n"
            new_string += f"s: {s}\n"
            new_string += f"r: {r}\n\n"
    
    return new_string


