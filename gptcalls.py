import time
import openai
import config

openai.api_key = config.openkey

user_prompt = None
old_user_prompt = None
context = [
    {"role": "system", "content": "Sprachassistent JARVIS erfunden von Carsten Schneider"},
]


def add_user_message(user_prompt):
    prompt = f"""
    {user_prompt}
    """
    global context
    context.append({"role": "user", "content": prompt +
                   ". Antworte in maximal 3 kurzen Sätzen."})


def add_assistent_message(gpt_response):
    global context
    context.append({"role": "assistant", "content": gpt_response})


def ask_chat_gpt(prompt):
    global old_user_prompt
    global user_prompt
    user_prompt = prompt
    if prompt == old_user_prompt or prompt == None:
        return None
    else:
        old_user_prompt = prompt
        try:
            add_user_message(user_prompt)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=context,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.3,
            )
            prompt = None
            add_assistent_message(
                response.choices[0].message["content"].strip())
            return response.choices[0].message["content"].strip()
        except Exception as e:
            print(f"Error generating response with ChatGPT: {e}")
            return "Es tut mir leid, es gab ein Problem bei der Antwortgenerierung."