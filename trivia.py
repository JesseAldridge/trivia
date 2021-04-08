import html, random, signal

import requests


def question_loop():
  class Results:
    def __init__(self):
      self.correct_count = 0
      self.incorrect_count = 0

  class TimeUpException(Exception):
    pass

  def interrupted(signum, frame):
    raise TimeUpException()
  signal.signal(signal.SIGALRM, interrupted)
  signal.alarm(5 * 60)

  results = Results()
  while True:
    resp = requests.get('https://opentdb.com/api.php?amount=1')
    question_dict = resp.json()['results'][0]

    '''
    example question_dict:
    {
      "category": "Science & Nature",
      "type": "multiple",
      "difficulty": "hard",
      "question": "Which of the following are cells of the adaptive immune system?",
      "correct_answer": "Cytotoxic T cells",
      "incorrect_answers": [
        "Dendritic cells",
        "Natural killer cells",
        "White blood cells"
      ]
    }
    '''

    raw_question_str = question_dict['question']
    clean_question_str = html.unescape(raw_question_str)
    correct_answer = question_dict['correct_answer']
    choices = [correct_answer] + question_dict['incorrect_answers']
    random.shuffle(choices)

    print(clean_question_str)
    for i, choice in enumerate(choices):
      print(f'{i + 1}) {choice}')

    while True:
      print('Choice:')
      try:
        choice = int(input())
        if choice < 1 or choice > 4:
          raise ValueError
        break
      except ValueError:
        print('invalid choice, please enter 1-4')
      except TimeUpException:
        return results

    if choice == choices.index(correct_answer) + 1:
      print('Correct!')
      results.correct_count += 1
    else:
      print('Incorrect')
      results.incorrect_count += 1
    print()

def main():
  results = question_loop()
  correct_count, incorrect_count = results.correct_count, results.incorrect_count
  print(f'{correct_count} correct, {incorrect_count} incorrect')
  print(f'final score: {correct_count - incorrect_count}')

if __name__ == '__main__':
  main()
