from openai import OpenAI
from config import settings


async def chat_gpt(house_info, vimshottari_dash):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""
    Ты астролог высокого уровня джйотиш, который отвечает на вопросы максимально подробно и максимально корректно.
    Расшифруй натальную карту на основе следующих данных:
    {house_info}
    {vimshottari_dash}
    **Задача:**
    - Проанализируй положение планет в домах, их силу и влияние.
    - Опиши ключевые тенденции в жизни человека.
    - Укажи, какие периоды (даши) будут наиболее важными.
    - Будь максимально точным и детализированным.
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "assistant", "content": prompt}],
        stream=False,
    )
    return response.choices[0].message.content
