import random
import os
import inspect
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
    def __init__(self, ind):
        super(CardStack, self).__init__()
        self.cards = []
        self.runlen = 0
        self.stackNum = ind
    
    def getCard(self, ind):
        return self.cards[ind]  

    def add(self, card):
        # print "Adding card with suit %d on stack %d. Height is %d. %s" % (card.suit, self.stackNum, self.height(), ("" if self.height() == 0 else ("Top stack has suit %d" % self.cards[-1].suit)))
        if self.height() == 0:
            self.runlen = 1
        elif self.cards[-1].shown and self.cards[-1].suit == card.suit + 1:
            self.runlen += 1
        else:
            self.runlen = 1
        self.cards.append(card)

    def height(self):
        return len(self.cards)

    def top(self):
        return self.cards[-1] if self.height() > 0 else None

    def runStart(self):
        return self.cards[-self.runlen] if self.height() > 0 else None

    def popRun(self):
        ret = self.cards[-self.runlen:]
        self.cards = self.cards[0:-self.runlen]
        return ret

    def addRun(self, run):
        self.cards += run
        self.runlen += len(run)

class Board(object):
    """docstring for Stacks"""
    def __init__(self):
        super(Board, self).__init__()
        self.cards = []
        for i in range(8):
            self.cards += [Card(i, False) for i in xrange(13)]
        random.shuffle(self.cards)
        self.stacks = [CardStack(i) for i in range(10)]
        for i in range(54):
            self.stacks[i % 10].add(self.cards[i])
            if i >= 44: 
                self.cards[i].flip()
        self.suits_left = 5
        
    def pprint(self):
        # os.system('cls' if os.name == 'nt' else 'clear')
        finished_stacks = 0
        level = 0
        labels = ""
        for i in range(10):
            labels += " " + str(i) + "(%d) " % self.stacks[i].runlen 
        print labels
        while finished_stacks < 10:
            row = ""
            for i in range(len(self.stacks)):
                if level < self.stacks[i].height():
                    row += self.stacks[i].getCard(level).to_str() 
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

    def move_stacks(self, src, dest):
        print "trying to move from %d to %d" % (src, dest)
        if src not in range(10) or dest not in range(10):
            return move_failure("Stack numbers out of range.")
        if self.stacks[dest].height() == 0:
            self.move_cards(src, dest)
        else:
            if self.stacks[dest].top().suit == self.stacks[src].runStart().suit + 1:
                self.move_cards(src, dest)
            else:
                return move_failure("Suits don't match.")
        return move_success()

    def move_cards(self, src, dest):
        self.stacks[dest].addRun(self.stacks[src].popRun())

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
            else: 
                move = raw_input(("Bad move. " if result[1] == "" else result[1]) + " " + prompt)
            result = self.parse_move(move)

        return self.score

    def parse_move(self, move):
        moveSplit = move.split(" ")
        moveName = moveSplit[0]
        if moveName in self.moves:
            m = self.moves[moveName]
            if len(moveSplit) == m.func_code.co_argcount:
                try:
                    # somewhat sloppy: only allow integer arguments to moves
                    return self.execute_move(m, [int(nstr) for nstr in moveSplit[1:]])
                except ValueError as e:
                    return move_failure("Invalid parameter types for move %s" % moveName)
            else:
                return move_failure("Invalid # parameters for move %s" % moveName)
        else:
            return move_failure("'%s' is not valid." % move)

    def execute_move(self, func, args):
        return func(*args)

    def quit(self):
        print "Goodbye!"
        return move_success()

    def hitme(self):
        return self.board.hitme()

    def transfer(self, src, dest):
        return self.board.move_stacks(src, dest)

def main():
    g = Game()
    score = g.play()
    print "Game Over. Score = " + str(score)
    return 0

main()