"""Generate teaching sentences for two extension categories: negation and grammar.

Output: negation_teaching.txt and grammar_teaching.txt (put them in corpus/).
Rules followed:
- Never copy eval prompts, answer lists or eval outputs.
- Avoid test phrases such as "one bird", "the dogs", "yesterday she".
- Drop combos that differ from a test story by only one noun.
- Negation stories stay on ONE line with no space after inner periods (".it"),
  because the notebook splits passages at "period + space".
"""
import itertools
import random
import re

random.seed(7)

# ---------------- NEGATION ----------------
names_f = ["lily", "zoe", "mia", "anna", "ruby", "ivy", "grace", "lucy", "ava", "rose"]
names_m = ["sam", "ben", "max", "tom", "jack", "kai", "dan", "ryan", "adam", "paul"]
colors = ["red", "blue", "green", "yellow", "white", "black", "brown", "pink", "gray", "purple"]
color_objs = ["cup", "bag", "shirt", "hat", "pen", "ball", "chair", "lamp", "book",
              "car", "bus", "coat", "wall", "bottle", "plate"]

neg = []

# Template 1: colour correction
for obj in color_objs:
    for c1, c2 in itertools.permutations(colors, 2):
        neg.append(f"the {obj} is not {c1} .it is {c2} .the {obj} is {c2} .")

# Template 2: state correction
state_pairs = [("clean", "dirty"), ("new", "old"), ("wide", "narrow"),
               ("broken", "fixed"), ("heavy", "light"), ("missing", "here")]
state_objs = ["box", "door", "window", "gate", "road", "table", "bridge", "room"]
for obj in state_objs:
    for a, b in state_pairs:
        for x, y in [(a, b), (b, a)]:
            neg.append(f"the {obj} is not {x} .it is {y} .the {obj} is {y} .")

# Template 3: open / closed for places
for obj in ["shop", "store", "bank", "office", "school", "market", "station", "kitchen", "window", "gate"]:
    for x, y in [("open", "closed"), ("closed", "open")]:
        neg.append(f"the {obj} is not {x} .it is {y} .the {obj} is {y} .")
        neg.append(f"today the {obj} is not {x} .it is {y} .")

# Template 4: "did not X ... Y instead" (ava is left out of these stories on purpose)
verbs = [("buy", "bought"), ("order", "ordered"), ("choose", "chose"), ("cook", "cooked"),
         ("eat", "ate"), ("pick", "picked"), ("want", "wanted")]
foods = ["tea", "milk", "rice", "bread", "juice", "coffee", "soup", "cake", "water", "pasta", "cheese", "eggs"]
buyers = [(n, "she") for n in names_f if n != "ava"] + [(n, "he") for n in names_m]
for name, pron in buyers:
    for v, vd in verbs:
        for f1, f2 in random.sample(list(itertools.permutations(foods, 2)), 6):
            neg.append(f"{name} did not {v} {f1} .{pron} {vd} {f2} .{name} {vd} {f2} .")

# Template 5: link to words the starter model already knows
people = ["nurse", "doctor", "teacher", "student", "customer", "driver"]
places = ["hospital", "school", "bank", "store", "market", "station", "office", "kitchen"]
for person in people:
    for p1, p2 in itertools.permutations(places, 2):
        pron = random.choice(["she", "he"])
        neg.append(f"the {person} is not at the {p1} .{pron} is at the {p2} .the {person} is at the {p2} .")

# Template 6: simple sentences so names enter the vocabulary
for n in names_f + names_m:
    neg.append(f"{n} is a student at the local school .")
    neg.append(f"{n} is not late today .")

# ---------------- GRAMMAR ----------------
sing = ["cat", "horse", "student", "nurse", "teacher", "apple", "car", "bus", "cup",
        "book", "child", "driver", "farmer", "bird", "dog"]
plur = ["cats", "horses", "students", "nurses", "teachers", "apples", "cars", "buses", "cups",
        "books", "children", "drivers", "farmers", "birds", "dogs"]
where = ["in the kitchen", "at the school", "near the station", "in the garden",
         "at the market", "on the road", "in the office", "at the hospital"]
adjs = ["happy", "busy", "small", "tired", "ready", "new", "late"]

gram = []

# Singular vs plural, present vs past
for s, pl in zip(sing, plur):
    a_or_an = "an" if s[0] in "aeiou" else "a"
    for w in where:
        if s != "bird":                      # avoid the test phrase "one bird"
            gram.append(f"one {s} is {w} .")
        gram.append(f"the {s} is {w} .")
        gram.append(f"{a_or_an} {s} was {w} yesterday .")
        if pl != "dogs":                     # avoid the test phrase "the dogs"
            gram.append(f"the {pl} are {w} .")
        gram.append(f"two {pl} are {w} .")
        gram.append(f"many {pl} were {w} yesterday .")
    for a in adjs:
        gram.append(f"this {s} is {a} .")
        gram.append(f"these {pl} are {a} .")
        gram.append(f"some {pl} were {a} .")

# Pronouns with am / is / are / were
for a in adjs:
    gram += [f"i am {a} today .", f"i am not {a} .", f"we are {a} .",
             f"they were {a} .", f"he is {a} .", f"she is {a} ."]

# Verb forms: walk / walked / walks / walking
verb_forms = [("walk", "walked", "walks", "walking"), ("visit", "visited", "visits", "visiting"),
              ("cook", "cooked", "cooks", "cooking"), ("clean", "cleaned", "cleans", "cleaning"),
              ("play", "played", "plays", "playing"), ("watch", "watched", "watches", "watching"),
              ("help", "helped", "helps", "helping"), ("open", "opened", "opens", "opening")]
targets = {"walk": ["to the park", "to the school", "to the station", "home"],
           "visit": ["the hospital", "the market", "the bank", "a friend"],
           "cook": ["rice", "soup", "pasta", "eggs"],
           "clean": ["the kitchen", "the room", "the table", "the car"],
           "play": ["football", "music", "a game", "with the cat"],
           "watch": ["a movie", "the birds", "the news", "the game"],
           "help": ["the teacher", "the nurse", "a customer", "the farmer"],
           "open": ["the door", "the window", "the shop", "the box"]}
subjects = ["he", "we", "they", "i"] + names_f[:6] + names_m[:6]   # no "she" after "yesterday"
for base, past, third, ing in verb_forms:
    for t in targets[base]:
        for sub in subjects:
            gram.append(f"yesterday {sub} {past} {t} .")
            if sub in ("we", "they", "i"):
                gram.append(f"every day {sub} {base} {t} .")
                gram.append(f"now {sub} {'am' if sub == 'i' else 'are'} {ing} {t} .")
            else:
                gram.append(f"every day {sub} {third} {t} .")
                gram.append(f"now {sub} is {ing} {t} .")
        gram.append(f"last week she {past} {t} .")
        gram.append(f"she likes to {base} {t} .")

# ---------------- Remove near copies of test stories ----------------
too_close = [r"is not red \.it is blue", r"did not buy tea \.\w+ bought milk", r"is not open \.it is closed"]
neg = [line for line in neg if not any(re.search(p, line) for p in too_close)]

neg, gram = sorted(set(neg)), sorted(set(gram))
with open("negation_teaching.txt", "w") as f:
    f.write("\n".join(neg) + "\n")
with open("grammar_teaching.txt", "w") as f:
    f.write("\n".join(gram) + "\n")
print("negation lines:", len(neg), "| grammar lines:", len(gram))
