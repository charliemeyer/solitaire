import random
import os
import inspect
card_names = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]

INIT_CARDS_DEALT = 54

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
        self.runlens = [0]
        self.stackNum = ind
    
    def getCard(self, ind):
        return self.cards[ind]  

    def add(self, newcards):
        # print "Adding card with suit %d on stack %d. Height is %d. %s" % (card.suit, self.stackNum, self.height(), ("" if self.height() == 0 else ("Top stack has suit %d" % self.cards[-1].suit)))
        if self.height() == 0:
            self.runlens[-1] = len(newcards)
        elif self.cards[-1].shown and self.cards[-1].suit == newcards[0].suit + 1:
            self.runlens[-1] += len(newcards)
        else:
            self.runlens.append(len(newcards)) # should always be 1
        self.cards += newcards

    def height(self):
        return len(self.cards)

    def top(self):
        return self.cards[-1] if self.height() > 0 else None

    def top_run(self):
        return self.cards[-self.runlens[-1]:]

    def runStart(self, run_length):
        return self.cards[-self.runlens[-1]] if run_length is None else self.cards[-run_length]

    def popRun(self, num_cards):
        ret = self.cards[-num_cards:]
        self.runlens[-1] -= num_cards
        if len(self.runlens) > 1 and self.runlens[-1] == 0:
            del self.runlens[-1]
        self.cards = self.cards[0:-len(ret)]
        if self.top() is not None:
            self.top().flip()
        return ret

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
            self.stacks[i % 10].add([self.cards[i]])
            if i >= 44: 
                self.cards[i].flip()
        self.suits_left = 5
        self.stacks_cleared = 0
        
    def pprint(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        level = 0
        labels = ""
        self.clear_finished_stacks()
        print "|".join(["_ %d _" % i for i in range(10)])
        finishedStacks = [0 for i in range(10)]
        while sum(finishedStacks) < 10:
            row = ""
            for i in range(10):
                if level < self.stacks[i].height():
                    row += self.stacks[i].getCard(level).to_str() 
                else:
                    row += "     "
                    finishedStacks[i] = 1
                row += " "
            print row
            level += 1

        print "      " * 9 + "X" * self.suits_left
        print "      " * 9 + "*" * self.stacks_cleared
        print "\n" + "_" * 60
        # if you've cleared 8 stacks, you're done!
        return self.stacks_cleared == 8


    def hitme(self):
        if self.suits_left > 0:
            if min([s.height for s in self.stacks]) > 0:
                for i in range(10):
                    card = self.cards[INIT_CARDS_DEALT + (5-self.suits_left)*10 + i]
                    card.flip()
                    self.stacks[i].add([card])
                self.suits_left -= 1
                return move_success()
            else: 
                return move_failure("Can't hitme with empty stacks.")
        else:
            return move_failure("No stacks left.")

    def move_stacks(self, src, dest, num_cards=None):
        if src not in range(10) or dest not in range(10):
            return move_failure("Stack numbers out of range.")
        if num_cards > len(self.stacks[src].top_run()):
            return move_failure("Source card number too high (max = %d)" % len(self.stacks[src].top_run()))
        if self.stacks[dest].height() == 0:
            self.move_cards(src, dest, num_cards)
        else:
            if self.stacks[dest].top().suit == self.stacks[src].runStart(num_cards).suit + 1:
                self.move_cards(src, dest, num_cards)
            else:
                return move_failure("Suits don't match.")
        return move_success()

    def move_cards(self, src, dest, num_cards=None):
        if num_cards is None:
            num_cards = len(self.stacks[src].top_run())
        self.stacks[dest].add(self.stacks[src].popRun(num_cards))

    def clear_finished_stacks(self):
        for s in self.stacks:
            if len(s.top_run()) == 13:
                s.popRun(13)
                self.stacks_cleared += 1

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
                done = self.board.pprint()
                if done:
                    print "Congratulations, you've won! :)"
                    break
                move = raw_input(prompt)
            else: 
                move = raw_input(("Bad move. " if result[1] == "" else result[1]) + " " + prompt)
            result = self.parse_move(move)

        return self.score

    def parse_move(self, move):
        moveSplit = move.split(" ")
        moveName = moveSplit[0]

        def valid_arg_nums(f):
            if m.func_defaults:
                return [m.func_code.co_argcount, m.func_code.co_argcount - len(m.func_defaults)]
            else:
                return [m.func_code.co_argcount]

        if moveName in self.moves:
            m = self.moves[moveName]
            if len(moveSplit) in valid_arg_nums(m):
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

    def transfer(self, src, dest, num_cards=None):
        return self.board.move_stacks(src, dest, num_cards)

def main():
    g = Game()
    score = g.play()
    print "Game Over. Score = " + str(score)
    return 0

main()