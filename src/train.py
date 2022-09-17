# https://huggingface.co/docs/transformers/perf_train_gpu_one
import numpy as np
from datasets import Dataset, load_from_disk

ds = load_from_disk("../data/datasets/ubffm_ft_debug_dataset")

MODEL_NAME = "bert-base-german-cased"

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

CATEGORY_FIELD = f"all_ner_tags"


def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["all_tokens"], truncation=True, is_split_into_words=True
    )

    labels = []
    for i, label in enumerate(examples[CATEGORY_FIELD]):
        word_ids = tokenized_inputs.word_ids(
            batch_index=i
        )  # Map tokens to their respective word.
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:  # Set the special tokens to -100.
            if word_idx is None:
                label_ids.append(-100)
            elif (
                word_idx != previous_word_idx
            ):  # Only label the first token of a given word.
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs


tokenized_ds = ds.map(tokenize_and_align_labels, batched=True)

from transformers import AutoModelForTokenClassification
from gpu_utls import print_gpu_utilization, print_summary

print_gpu_utilization()

model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME, num_labels=len(ds.features[CATEGORY_FIELD].feature.names)
)

print_gpu_utilization()

from transformers import DataCollatorForTokenClassification

data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

# https://huggingface.co/docs/transformers/training
import numpy as np
import evaluate

metric = evaluate.load("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


default_args = {
    "output_dir": "tmp",
    "evaluation_strategy": "steps",
    "num_train_epochs": 1,
    "log_level": "error",
    "report_to": "none",
}

from transformers import TrainingArguments, Trainer, logging

logging.set_verbosity_error()

training_args = TrainingArguments(
    per_device_train_batch_size=1,
    # optim="adafactor",
    optim="adamw_torch",
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    do_eval=False,
    output_dir="lang-sci-press_ft_debug_training",
    no_cuda=True,
)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_ds,
    eval_dataset=tokenized_ds,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

result = trainer.train()
print_summary(result)
