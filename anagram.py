import zmq
import random

EASY = 1
MEDIUM = 2
HARD = 3
DIFFICULTIES = {"easy": EASY, "medium": MEDIUM, "hard": HARD}
FILES = [None, "easy_words.txt", "medium_words.txt", "hard_words.txt"]


class AnagramChallenge:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.port_number = 5001
        self.socket.bind(f"tcp://*:{self.port_number}")

        self.difficulty = EASY
        self.challenge = None
        self.actual_answer = None
        self.user_answer = None

    def main_loop(self):
        while True:
            message = self.socket.recv_pyobj()
            if message[0] == "request":
                self.reset()
                success = self.parse_request(message)

                if not success:
                    self.socket.send_pyobj(["error", "Error Parsing Request"])
                    continue

                self.generate_challenge()
                print(f"Generated Challenge - Challenge: {self.challenge} - Possible Answer: {self.actual_answer}")

                self.socket.send_pyobj(["problem", self.challenge])
            elif message[0] == "response" and self.actual_answer:
                success = self.parse_response(message)
                if not success:
                    self.socket.send_pyobj(["error", "Error Parsing Response"])
                    continue

                success = self.check_answer()

                self.socket.send_pyobj(["answer", 1 if success else 0, self.actual_answer])
                self.reset()
            else:
                self.socket.send_pyobj(["error", "Error Parsing Message"])

    def reset(self):
        self.difficulty = EASY
        self.challenge = None
        self.actual_answer = None
        self.user_answer = None

    def parse_request(self, request):
        if request[0] != "request":
            print("First index not 'request'")
            return False
        if request[1] and request[1].lower() in DIFFICULTIES:
            self.difficulty = DIFFICULTIES[request[1].lower()]
        return True

    def generate_challenge(self):
        file = FILES[self.difficulty]
        with open(file, 'r') as f:
            words = f.readlines()
        self.actual_answer = random.choice(words).strip()

        self.challenge = list(self.actual_answer)
        random.shuffle(self.challenge)
        self.challenge = str(self.challenge)

    def parse_response(self, response):
        if response[0] != "response":
            print("First index not 'response'")
            return False
        if response[1]:
            self.user_answer = response[1]
            return True
        print("Missing answer")
        return False

    def check_answer(self):
        file = FILES[self.difficulty]
        with open(file, 'r') as f:
            words = f.readlines()
        words = [x.strip() for x in words]
        # Optimization: Binary Search
        if self.user_answer in words:
            return True
        return False


def main():
    challenge = AnagramChallenge()
    challenge.main_loop()


if __name__ == '__main__':
    main()