# from huggingface_hub import login

# login("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")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_name = "meta-llama/Llama-3.1-8B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,               
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model.config.use_cache = False

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

from transformers import pipeline

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

prompts = [
    "When is the earliest train from Ljubljana to Milano today?",
    "What will the weather be like in Barcelona for the next 3 days?",
    "Can you suggest a romantic weekend in Europe for a couple?",
    "What clothes should I pack for the next 3 days in Rome?",
    "I’m visiting Barcelona with friends for 3 days and we want beaches, nightlife, and fun activities. What should we do?"
]

results = []
for prompt in prompts:
    response = chat(
        user_message="Find me a complete train route from Ljubljana to Munich tomorrow."
    )
    results.append((prompt, response))

print("======= RESULTS =======\n")
for prompt, result in results:
    print(prompt)
    print(result, '\n')
print("=======================")