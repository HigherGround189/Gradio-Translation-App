from transformers import MarianMTModel, MarianTokenizer

class MarianManager:

    def __init__(self):
      self.model_name = "Helsinki-NLP/opus-mt-en-zh"
      self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
      self.model = MarianMTModel.from_pretrained(self.model_name)

    def translate(self, src_text: str) -> str:
        translated = self.model.generate(**self.tokenizer(text=src_text, return_tensors="pt", padding=True))
        tgt_text = [self.tokenizer.decode(t, skip_special_tokens=True) for t in translated]
        return tgt_text