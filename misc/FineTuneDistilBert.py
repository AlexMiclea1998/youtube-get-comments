import torch

torch.cuda.is_available()
from datasets import load_dataset


dataset = load_dataset('csv', data_files={'train': ['Book2.csv'], 'test': 'Book2.csv'})

train_dataset = dataset["train"].shuffle(seed=42).select([i for i in list(range(180))])
test_dataset = dataset["test"].shuffle(seed=42).select([i for i in list(range(40))])


from transformers import AutoTokenizer, AutoModel, BertTokenizer, BertForPreTraining, pipeline

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")


def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True, padding=True)


tokenized_train = train_dataset.map(preprocess_function, batched=True)
tokenized_test = test_dataset.map(preprocess_function, batched=True)

print(tokenized_test)

from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

import numpy as np
from datasets import load_metric


def compute_metrics(eval_pred):
    load_accuracy = load_metric("accuracy")
    load_f1 = load_metric("f1")

    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = load_accuracy.compute(predictions=predictions, references=labels)["accuracy"]
    f1 = load_f1.compute(predictions=predictions, references=labels)["f1"]
    print("F1:", f1)
    print("Accuracy:", accuracy)
    return {"accuracy": accuracy, "f1": f1}


from transformers import TrainingArguments, Trainer

repo_name = "finetuning-sentiment-model-1500-samples"

training_args = TrainingArguments(
    output_dir=repo_name,
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=2,
    weight_decay=0.01,
    save_strategy="epoch",
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,

)


trainer.train()
trainer.evaluate()
# F1: 0.6538461538461539
# Accuracy: 0.55




