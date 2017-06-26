import random
import os
card_names = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]

INIT_CARDS_DEALT = 44

def move_success():
    return (True, "")

def move_failure(message="Error."):
    return (False, message)

class Card(object):
    """docstring for Card"""
    def __init__(self, suit, shown=False):
        super(Card, self).__init__()
        self.suit = suit
        self.shown = shown 

    def to_str(self):
        if self.shown:
            return "| " + str(card_names[self.suit]) + " |"
        else:
            return "| X |"

    def pprint(self):
        return ".___.\n" + self.to_str() + "\n|___|"

    def flip(self):
        self.shown = True

class CardStack(object):
    """docstring for CardStack"""
    def __init__(self):
        super(CardStack, self).__init__()
        self.cards = []
    
    def get_card(self, ind):
        return self.cards[ind]  

    def add(self, card):
        self.cards.append(card)  

    def height(self):
        return len(self.cards)

class Board(object):
    """docstring for Stacks"""
    def __init__(self):
        super(Board, self).__init__()
        self.cards = []
        for i in range(8):
            self.cards += [Card(i, False) for i in xrange(13)]
        random.shuffle(self.cards)
        self.stacks = [CardStack() for i in range(10)]
        for i in range(54):
            self.stacks[i % 10].add(self.cards[i])
            if i >= 44: 
                self.cards[i].flip()
        self.suits_left = 5
        
    def pprint(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        finished_stacks = 0
        level = 0
        labels = ""
        for i in range(10):
            labels += "  " + str(i) + "   "
        print labels
        while finished_stacks < 10:
            row = ""
            for i in range(len(self.stacks)):
                if level < self.stacks[i].height():
                    row += self.stacks[i].get_card(level).to_str() 
                else:
                    row += "     "
                    finished_stacks += 1
                row += " "
            print row
            level += 1

        print "      " * 9 + "X" * self.suits_left
        print "\n" + "_" * 60

    def hitme(self):
        if self.suits_left > 0:
            for i in range(10):
                card = self.cards[INIT_CARDS_DEALT + (5-self.suits_left)*10 + i]
                card.flip()
                self.stacks[i].add(card)
            self.suits_left -= 1
            return move_success()
        else:
            return move_failure("No stacks left.")


class Game(object):
    """docstring for Game"""
    def __init__(self):
        super(Game, self).__init__()
        self.moves = {"quit": self.quit,
                                  "h": self.hitme,
                                  "m": self.transfer}
        self.score = 0
        self.board = Board()

    def play(self, human=True):
        move = ""
        prompt = "Enter a move. (" + ", ".join(self.moves) + "): "
        result = move_success()
        print "Welcome to Solitaire"
        while(move != "quit"):
            if result[0]:
                self.board.pprint()
                move = raw_input(prompt)
                result = self.execute_move(move)
            else: 
                move = raw_input(("Bad move. " if result[1] == "" else result[1]) + " " + prompt)

        return self.score

    def execute_move(self, move):
        if move in self.moves:
            m = self.moves[move]
            return m()
        else:
            return move_failure("'%s' is not valid. " % move)

    def quit(self):
        print "Goodbye!"
        return move_success()

    def hitme(self):
        return self.board.hitme()

    def transfer(self):
        return move_success()

def main():
    g = Game()
    score = g.play()
    print "Game Over. Score = " + str(score)
    return 0

main()