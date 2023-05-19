import pandas as pd
import numpy as np
import csv
import os
import random
import genanki

n5 = pd.read_csv('./kanji/n5.txt', sep="\t", header=None)
n4 = pd.read_csv('./kanji/n4.txt', sep="\t", header=None)
n3 = pd.read_csv('./kanji/n3.txt', sep="\t", header=None)

dataset = pd.concat([n5, n4], ignore_index=True)
dataset = dataset[dataset.columns[0:10]]

dataset = pd.DataFrame({
    "Kanji": dataset.iloc[:,0],
    "Hanviet": dataset.iloc[:, 6],
    "Examples": dataset.iloc[:,9]
})


def all_includes(row, kanjis):
  tokens = list(row["Example"])
  for token in tokens:
    if token not in kanjis:
      return False

  return True

def to_hanviet(example, dataset):
  tokens = list(example)
  subset = dataset[dataset["Kanji"].isin(tokens)]

  hanviet = [list(subset[subset["Kanji"] == token]["Hanviet"])[0] for token in tokens]

  return ' - '.join(hanviet).title()

def tokenize(example):
  tokens = example.split(":")

  if len(tokens) == 2:
    key = tokens[0].strip()
    mean = tokens[1].strip()

    kanjis = key.split("(")[0].strip()
    romajis = key.split("(")[1].replace(")", "").strip()

    return [kanjis, romajis, mean]
  else:
    return False

def flatten_row(row, dataset):
  examples = list(filter(lambda x: ":" in x, row['Examples'].split("<br>")))

  details = pd.DataFrame(filter(lambda x: x is not False, list(map(tokenize, examples))), columns=["Example", "Reading", "Meaning"])

  details = details[details.apply(lambda x: all_includes(x, list(dataset.iloc[:, 0])), axis=1)]
  # details["Hanviet"] = details["Example"].apply(lambda x: map(lambda y:  list(x)), axis=1)
  details["Hanviet"] = details["Example"]
  details["Hanviet"] = details["Example"].apply(lambda x: to_hanviet(x, dataset))
  kanjis = [row["Kanji"]] * len(details)

  rows = pd.DataFrame({
    "Kanji": kanjis,
    "Example": details["Example"],
    "Hanviet": details["Hanviet"],
    "Reading": details["Reading"],
    "Meaning": details["Meaning"]
  })
  rows = rows.reset_index(drop=True)

  return rows


count = 0
notes = pd.DataFrame({}, columns=["Kanji", "Example", "Hanviet", "Reading", "Meaning"])
for index, row in dataset.iterrows():
  notes = pd.concat([notes, flatten_row(row, dataset)], ignore_index=True)

notes = notes.drop_duplicates(subset="Example", keep="first")
notes.reset_index(drop=True)

my_model = genanki.Model(
  random.randrange(1 << 30, 1 << 31),
  'Kanji Example',
  fields=[
    {'name': 'Example'},
    {'name': 'Hanviet'},
    {'name': 'Reading'},
    {'name': 'Meaning'},
  ],
  css="""
    .card { text-align: center; }
    .card-back-content { text-align: left; padding: 10px 20px }
    .example { font-size: 32px; line-height: 100%; }
    .example-container + .example-container { margin-top: 20px; }
  """,
  templates=[
    {
      'name': 'Card 1',
      'qfmt': """
        <div style="card">
          <div class="example">
            {{Example}}
          </div>
        </div>
      """,
      'afmt': """
        <div class="card card-back">
          <div class="example">
            {{Example}}
          </div>
            <strong>{{Reading}}</strong>
            <br>
            {{Hanviet}}
            <hr id="answer">
          <div class="card-back-content">
            {{Meaning}}
          </div>
        </div>
      """,
    },
    {
      'name': 'Card 2',
      'qfmt': """
        <div style="card">
          <div class="example">
            {{Reading}}
          </div>
        </div>
      """,
      'afmt': """
        <div class="card card-back">
          <div class="example">
            {{Reading}}
          </div>
            <strong>{{Example}}</strong>
            <br>
            {{Hanviet}}
            <hr id="answer">
          <div class="card-back-content">
            {{Meaning}}
          </div>
        </div>
      """,
    },
  ])

my_deck = genanki.Deck(
  random.randrange(1 << 30, 1 << 31),
  'Kanji Examples',
)

for index, row in notes.iterrows():
  file_path = "./mazii/" + row["Example"] + ".html"

  meaning_viet = row["Meaning"]
  if os.path.isfile(file_path):
    meaning_viet = open(file_path, "r").read()
    meaning_viet = meaning_viet.replace("<!--", "")
    meaning_viet = meaning_viet.replace("-->", "")
  else:
    print(file_path)

  anki_note = genanki.Note(
    model=my_model,
    fields=[row["Example"], row["Hanviet"], row["Reading"], meaning_viet]
  )

  my_deck.add_note(anki_note)

genanki.Package(my_deck).write_to_file("deck.apkg")