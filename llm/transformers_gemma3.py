import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from bulk_chain.core.llm_base import BaseLM


class Gemma3(BaseLM):
    """
      Gemma3: https://blog.google/technology/developers/gemma-3/

      This is a non-pipeline / Native transformers API-based wrapper for Gemma3 model series with batching support.

      Input specifics:
      - [SUPPORTED] Text string, such as a question, a prompt, or a document to be summarized
      - [NOT SUPPORTED BY THIS PROVIDER] Images, normalized to 896 x 896 resolution and encoded to 256 tokens each
      - Total input context of 128K tokens for the 4B, 12B, and 27B sizes, and 32K tokens for the 1B size
    """

    def __init__(self, model_name="google/gemma-3-1b-it", temp=0.1, device='cuda',
                 max_new_tokens=None, api_token=None, **kwargs):
        super(Gemma3, self).__init__(name=model_name, support_batching=True, **kwargs)
        self.__device = device
        self.__model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", token=api_token)
        self.__max_new_tokens = max_new_tokens
        self.__model.to(device)
        self.__tokenizer = AutoTokenizer.from_pretrained(model_name, token=api_token)
        self.__temp = temp

    def ask(self, batch):
        inputs = self.__tokenizer(
            [
                {
                    {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
                    {"role": "user", "content": [{"type": "text", "text": p}]}
                } 
                for p in batch
            ], 
            return_tensors="pt", 
            padding=True, 
            truncation=True)
        inputs.to(self.__device)
        outputs = self.__model.generate(**inputs, max_new_tokens=self.__max_new_tokens, temperature=self.__temp, do_sample=True)
        return self.__tokenizer.batch_decode(outputs, skip_special_tokens=True)
