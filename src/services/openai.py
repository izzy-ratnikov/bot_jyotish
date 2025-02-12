from openai import OpenAI
from src.dispatcher.dispatcher import openai_api_key


async def chat_gpt(house_info):
    client = OpenAI(api_key=openai_api_key)

    prompt = f"""
    Ты астролог высокого уровня джйотиш, который отвечает на вопросы максимально подробно и максимально корректно.
    Расшифруй натальную карту на основе следующих данных:
    {house_info}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "assistant", "content": prompt}],
        stream=False,
    )
    return response.choices[0].message.content
