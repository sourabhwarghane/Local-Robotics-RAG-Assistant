import ollama

MODEL_NAME = "qwen3:1.7b"


class LocalLLM:

    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name

        print(
            f"Using local LLM: "
            f"{self.model_name}"
        )

    def generate(self, prompt):
        response = ollama.chat(
            model=self.model_name,

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],

            options={
                "temperature": 0.0,
                "num_ctx": 2048,
            },
            keep_alive="2m",
        )

        return response["message"]["content"]
