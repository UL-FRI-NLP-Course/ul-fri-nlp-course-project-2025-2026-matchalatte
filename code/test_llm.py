from huggingface_hub import login

login("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")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_name = "meta-llama/Llama-3.1-8B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,               # Store weights in 4-bit
    bnb_4bit_quant_type="nf4",       # NormalFloat 4-bit — optimal for normally-distributed weights
    bnb_4bit_use_double_quant=True,  # Quantise the quantisation constants too (~0.37 bits saved/param)
    bnb_4bit_compute_dtype=torch.bfloat16,  # Upcast to bfloat16 for matrix multiplications
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",        # Distribute layers across available GPUs automatically
    trust_remote_code=True,
)
model.config.use_cache = False

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

# Llama-3 has no dedicated pad token — use eos_token as pad
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

from transformers import pipeline

# Create the pipeline without generation parameters — the pipeline manages
# its own GenerationConfig internally; passing one at construction causes a conflict.
generator = pipeline(
    model=model,
    tokenizer=tokenizer,
    task="text-generation",
)

def chat(user_message, system_message="""You are a helpful travel assistant.
You give clear, practical travel advice including itineraries, tips, and recommendations.
Keep answers structured and easy to follow.""",
         temperature=0.1, max_new_tokens=300, repetition_penalty=1.1):
    """Format a message using the model's chat template and return the assistant reply."""
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user",   "content": user_message},
    ]
    response = generator(
        messages,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        repetition_penalty=repetition_penalty,
        do_sample=True,
    )
    return response[0]["generated_text"][-1]["content"]

print(torch.cuda.is_available())

msg0 = "I’m visiting Barcelona with friends and we want beaches, nightlife, and fun activities. What should we do?"
msg1 = "What’s the best way to travel from Amsterdam to Brussels?"
msg2 = "Can you suggest a romantic weekend in Europe for a couple?"
msg3 = "What are the best budget-friendly cities to visit in Europe?"
msg4 = "When is the earliest train from Ljubljana to Milano today"

response = chat(
    user_message=msg4
)
print()
print(response)