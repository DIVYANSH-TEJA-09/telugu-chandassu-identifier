from telugu_chandas.engine import ChandasEngine
from telugu_chandas.models import Weight

text = """అమితాంభోజభవాండభాండనిలయంబైయుండు నీ యంతరం-
గము పట్టెంతయొ దానికింక బహిరంగం బెట్టిదో సూక్ష్మత-
త్త్వము దానంతకుమీఁద నేమివిధమో తానిట్టి నీ పెంపుమా-
ర్గము నీకైన నచింత్య మెట్లొరుఁ డెఱుంగం జాలు సర్వేశ్వరా!"""

engine = ChandasEngine()
tokens = engine.analyze(text)

# Find 'సూక్ష్మత-' token
target_token = None
next_token_word = None

for i, token in enumerate(tokens):
    if "సూక్ష్మత" in token.text:
        target_token = token
        # Find next word
        for j in range(i + 1, len(tokens)):
            if tokens[j].is_word:
                next_token_word = tokens[j]
                break
        break

print(f"Target Token Text: '{target_token.text}'")
print(f"Has Hyphen: {'-' in target_token.text}")

print("\nTarget Aksharas:")
for ak in target_token.aksharas:
    print(f"  {ak.text} : {ak.weight}")

if next_token_word:
    print(f"\nNext Word: '{next_token_word.text}'")
    first_ak = next_token_word.aksharas[0]
    print(f"  First Akshara: '{first_ak.text}'")
    print(f"  Components: {first_ak.components}")
    print(f"  Onset Count: {first_ak.onset_hallulu_count}")
else:
    print("Next word not found!")
