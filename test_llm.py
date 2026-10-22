from app.llm import llm

response = llm.invoke("Say hello to the world")

print(response.text)