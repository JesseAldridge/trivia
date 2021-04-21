#!/usr/bin/env python3
import html, random, signal, sys, os, csv, datetime

import requests

# changed from 5 -> 3 minutes on 4/20/21; first test the next day


def question_loop(is_test):
  class Results:
    def __init__(self):
      self.correct_count = 0
      self.incorrect_count = 0

  class TimeUpException(Exception):
    pass

  def interrupted(signum, frame):
    raise TimeUpException()
  signal.signal(signal.SIGALRM, interrupted)
  signal.alarm(5 if is_test else 2 * 60)

  results = Results()
  while True:
    try:
      ask_question(results)
    except TimeUpException:
      return results

def ask_question(results):
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
  correct_answer = html.unescape(question_dict['correct_answer'])
  incorrect_answers = [html.unescape(s) for s in question_dict['incorrect_answers']]
  choices = [correct_answer] + incorrect_answers
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

  if choice == choices.index(correct_answer) + 1:
    print('Correct!')
    results.correct_count += 1
  else:
    print('Incorrect')
    results.incorrect_count += 1
  print(results.correct_count, results.incorrect_count)
  print()

def main():
  is_test = 'test' in sys.argv
  results = question_loop(is_test)
  correct_count, incorrect_count = results.correct_count, results.incorrect_count
  print(f'\n{correct_count} correct, {incorrect_count} incorrect')
  print(f'final score: {correct_count - incorrect_count}')

  data_path = os.path.expanduser(f'~/trivia_scores{"_test" if is_test else ""}.csv')
  if not os.path.exists(data_path):
    with open(data_path, 'w') as f:
      writer = csv.writer(f)
      writer.writerow(['datetime', 'score', 'correct', 'incorrect'])

  with open(data_path, 'a') as f:
    writer = csv.writer(f)
    writer.writerow([
      datetime.datetime.now(datetime.timezone.utc).astimezone(),
      correct_count - incorrect_count,
      correct_count,
      incorrect_count,
    ])

  print('result written to:', data_path)

if __name__ == '__main__':
  main()
