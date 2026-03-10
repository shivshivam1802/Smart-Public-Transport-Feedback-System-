from transformers import BertTokenizer, BertForSequenceClassification
import torch

labels = ["delay","overcrowding","cleanliness","staff","safety","infrastructure"]
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=len(labels),
)

def predict_issues(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    probs = torch.sigmoid(model(**inputs).logits)[0]
    return [labels[i] for i,p in enumerate(probs) if p > 0.5]
