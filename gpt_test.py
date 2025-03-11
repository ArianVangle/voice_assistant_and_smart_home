from g4f.client import Client
import g4f
client = Client()
def gpt4o_ans(text: str):

    response = client.chat.completions.create(
        model=g4f.models.gpt_4o,
        messages=[{"role": "user", "content": text +  '(если будут числа в твоем ответе, пиши их словами, дай краткий ответ. Если же в ответе втстретятся английские слова, то пиши их русскими буквами как они читаются)'}],
        max_tokens=30,
        web_search=True,
    )
    return response.choices[0].message.content

