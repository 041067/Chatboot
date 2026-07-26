import os
from typing import Optional
from groq import Groq


class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("ERRO: A chave GROQ_API_KEY nao foi encontrada no arquivo .env!")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)

    def is_available(self) -> bool:
        return self.client is not None

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> tuple[str, int, int]:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY nao configurada. Verifique o arquivo backend/.env.")

        completion = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        response = completion.choices[0].message.content

        usage = completion.usage
        tokens_sent = usage.prompt_tokens if usage else 0
        tokens_received = usage.completion_tokens if usage else 0

        return response, tokens_sent, tokens_received
