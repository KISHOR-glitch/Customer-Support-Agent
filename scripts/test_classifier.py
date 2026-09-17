import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.intents.classifier import predict_intent


print("SupportLens Keyword Classifier")
print("Type 'exit' to stop.")
print("-" * 50)

while True:
    text = input("\nEnter customer message: ")

    if text.lower() == "exit":
        break

    intent, confidence = predict_intent(text)

    print(f"Predicted intent : {intent}")
    print(f"Confidence       : {confidence}")