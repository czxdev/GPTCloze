import openai
from tenacity import retry, stop_after_attempt

# Use GPT series from OpenAI
model_name = "gpt-3.5-turbo" # "gpt-3.5-turbo" "gpt-4o"
client = openai.OpenAI(api_key="XXXXX")
# Use other OpenAI-compatible API
# model_name = "qwen-plus" # "qwen-turbo" "qwen-plus" "qwen-max"
# client = openai.OpenAI(base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

@retry(stop=stop_after_attempt(3), reraise=True)
def run_conversation(content:str):
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "system", "content": "You are a helpful assistent completing tasks without outputing extra responses that reveals you are a chatbot."},
                {"role": "user", "content": content}]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.4
    )
    response_message = response.choices[0].message
    return response_message

if __name__ == '__main__':
    prompt = r'''
You are helping an English learner to generate a memory card with an English sentence and its Chinese translation. You will be provided a target sentence, a target expression and the english definition of the target expression. You have to do the following things: 1. Repeat the target sentence with the target expression embraced in the sentecne with {{}}. 2. Translate the target sentence into Chinese and embrace the Chinese translation of the target expression with {{}} in the sentence translation. 3. translate the target expression according to its english definition
Here is an example for your task:
Inputs:
Target sentence: He manifested a pleasing personality on stage. 
Target expression: manifest
Definition: to show something clearly, especially a feeling, an attitude or a quality

Outputs:
Sentence: He {{manifested}} a pleasing personality on stage. 
Sentence Translation: 他在舞台上{{展现出}}迷人的个性。
Definition Translation: 显现出

Extra Demands: Never add any irrelated prompt to the aforementioned tasks. Never repeat the task descriptions in the response. Response of each task is prefixed with 'Sentence:', 'Sentence Translation:', and 'Definition Translation:'.

Input:
Target sentence: The announcement unleashed a storm of protest from the public.
Target expression: unleash
Definition: to suddenly let a strong force, emotion, etc. be felt or have an effect
'''
    print(run_conversation(prompt).content)
    