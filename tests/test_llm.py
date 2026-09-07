from src.llm import LocalLLM


llm = LocalLLM()

answer = llm.generate("Explain ROS 2 in two short sentences.")

print("\nANSWER:\n")
print(answer)
