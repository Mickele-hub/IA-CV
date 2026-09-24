from datasets import load_dataset

ds = load_dataset("cnamuangtoun/resume-job-description-fit")
print(ds)
print(ds["train"][0])  # regarde à quoi ressemble une ligne