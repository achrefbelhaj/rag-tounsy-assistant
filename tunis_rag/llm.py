"""LLM local chargé directement dans Python (Hugging Face Transformers).

Interface minimale : une seule méthode generate(system, user). Tout autre LLM (API en
ligne, Ollama...) peut la remplacer sans toucher à rag.py.
"""


class LLMUnavailable(RuntimeError):
    """Le modèle n'a pas pu être chargé ou exécuté."""


class QwenClient:
    def __init__(self, model_name: str, max_new_tokens: int = 300):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self._tokenizer = None
        self._model = None

    def _load(self):
        if self._model is None:  # chargement paresseux : fait au premier appel seulement
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer

                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name, torch_dtype="auto", device_map="auto")
                self._model.eval()
            except Exception as exc:
                raise LLMUnavailable(
                    f"Impossible de charger le modèle « {self.model_name} » "
                    f"(connexion internet au premier lancement ? mémoire suffisante ?).") from exc
        return self._tokenizer, self._model

    def generate(self, system: str, user: str) -> str:
        tokenizer, model = self._load()   # lève LLMUnavailable si le chargement échoue
        import torch

        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": user}]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False,
                                               add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=self.max_new_tokens,
                                    do_sample=False,  # réponses stables, pas de créativité
                                    pad_token_id=tokenizer.eos_token_id)
        generated = output[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(generated, skip_special_tokens=True).strip()
