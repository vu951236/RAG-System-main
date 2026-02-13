import random
import re

def train_markov(text, model):
    words = re.findall(r'\w+', text.lower())
    if len(words) < 3:
        return

    for i in range(len(words) - 2):
        state = (words[i], words[i+1])
        nxt = words[i+2]
        if state not in model:
            model[state] = {}
        model[state][nxt] = model[state].get(nxt, 0) + 1

def generate_answer(seed_text, model, max_len=50):
    if not model:
        return "Tôi không tìm thấy đủ dữ liệu trong tài liệu để trả lời."

    seed_words = re.findall(r'\w+', seed_text.lower())
    curr_state = None

    # Thử tìm seed từ câu hỏi
    for i in range(len(seed_words) - 1):
        potential = (seed_words[i], seed_words[i+1])
        if potential in model:
            curr_state = potential
            break

    if not curr_state:
        curr_state = random.choice(list(model.keys()))

    result = [curr_state[0], curr_state[1]]

    for _ in range(max_len):
        if curr_state in model:
            choices = list(model[curr_state].keys())
            weights = list(model[curr_state].values())
            nxt_word = random.choices(choices, weights=weights, k=1)[0]
            result.append(nxt_word)
            curr_state = (curr_state[1], nxt_word)
        else:
            # Nếu cụm từ bị cụt, lấy ngẫu nhiên một trạng thái mới có từ cuối cùng
            possible_next = [s for s in model.keys() if s[0] == curr_state[1]]
            if possible_next:
                curr_state = random.choice(possible_next)
            else:
                break

    output = " ".join(result).strip()
    return output.capitalize() + "."