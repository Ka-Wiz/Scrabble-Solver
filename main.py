import string
import random
import copy
import time
import tkinter.filedialog

# globals, pay no mind
lscore = {'_': 0, 'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1,
          'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10}
lstring = 'AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ__'
racks = None
prnt = True


def pull_rack():
    if runs == 'm': return rack
    if racks is not None: return list(racks.pop())
    bag = list(lstring)
    pull = []
    for n in range(7):
        random.shuffle(bag)
        pull.append(bag.pop())
    return pull


if __name__ == '__main__':
    print('\nwelcome to scrabble first word placer 9001!!\nthis program picks the a strategic first play!')
    print('(which may or may not be the highest scoring, see program code for details!)\n')

    # INFORMED SEARCH: we immediately and IMMENSELY reduce our search space to only 267,751 valid possibilities...
    file = open('SOWPODS_complete.txt', 'r').read().split('\n')

    runs = input('how many random racks should we test? (f to use a file, m to manually enter a rack): ')
    run = 0
    total_time = 0.0

    if runs == 'f':
        racks = tkinter.filedialog.askopenfile(mode='r').read().split('\n')
        while '' in racks: racks.remove('')
        racks.reverse()
        runs = len(racks)
    elif runs != 'm':
        runs = int(runs) if runs != '' else 1
        if runs > 1 and input('print outputs? y/n: ') != 'y': prnt = False
    else:
        rack = list(input('input letters or _ (hint: any number of characters >:) ) ').upper())
    print('running.........\n')

    while True:
        # let's see what we have to work with shall we?
        rack = pull_rack()
        racklen = len(rack)
        counts = {}
        for l in rack: counts[l] = counts.get(l, 0) + 1
        blanks = True if counts.get('_', 0) > 0 else False

        # start measuring, "thinking" logic starts here
        start = time.perf_counter()

        # CONSTRAINT SATISFACTION: we further prune search space by discarding options that break our constraints,
        # taking all the early outs we can to reduce execution time...
        words = []
        for w in file:
            # starting with the easiest one to compute: whether it requires more than our tray...
            # (could be expedited with a preprocessed list of words by letter count)
            if len(w) > racklen: continue

            # or letters/quantities of letters we do not have...
            # (also could be a preprocessed db of words by tray combination lmao (not permutation, order irrelevant ;) )
            # https://math.stackexchange.com/questions/243685/ says 3199724 possible starting trays.
            # okay so we assign each word an ID to minimize storage size, each tray has a list of IDs........)
            temp_cnt = copy.copy(counts)
            valid = True
            for l in w:
                has = temp_cnt.get(l, 0)
                if has == 0:
                    has = temp_cnt.get('_', 0)  # keeping in mind that we can always replace a letter if we have a blank
                    if has > 0:
                        w = w.replace(l, l.lower(), 1)  # ...but don't score it!! (we use lowercase to represent a blank)
                        l = '_'
                    else:
                        valid = False
                        break
                temp_cnt[l] = has - 1
            if valid: words.append(w)

        # now that we have pruned an INCREDIBLE amount of space to only the words we can make, simply brute force
        scores = [(sum(lscore.get(l, 0) for l in w), w) for w in words]
        scores.sort(reverse=True)

        if len(scores) > 0:
            # and now some scrabble strategy, go for highest score but prefer shortest word to limit opponent options
            # (we are willing to sacrifice a few points if it makes a word 5 characters or less, see below...)
            thresh = scores[0][0] - 2
            win = scores[0]
            cand = []
            for w in scores:
                if w[0] < thresh: break
                wlen = len(w[1])
                winlen = len(win[1])
                if wlen <= winlen and w[0] == win[0] or winlen > 5 and wlen <= 5:
                    win = w
                    cand.append(w)
            cand.sort(key=lambda w: len(w[1]))

            # second bit of strategy, board is symmetrical but double word squares exist on and beyond columns 5 and 11.
            # deny orthogonal access to as many as possible by keeping words in center, words of 5 or less characters
            # can deny them completely! worth a point or two i think~
            column = 8 - int(len(win[1]) / 2)
            # possible expansions here: foreach placement we can make, examine domain of opponent moves (we can do normal turn
            # logic to figure, just use remaining letters in bag as big 'tray') attenuated by probability of being able to make
            # them (calc'd from known letter distribution) and make placement with least opponent utility (minmax anyone?)
            # also some easier stuff like if word is greater than 5 letters, try to put least valuable letter in double word
            # column so opponent can't capitalize on it too well

        end = time.perf_counter()
        total_time += end-start
        run += 1

        # ANYWAY, the coup de grâce!
        if prnt or run == runs:
            if not prnt: print('last ', end='')
            print('rack: ' + ''.join(rack))
            if len(scores) == 0:
                print('this rack doesn\'t have ANY valid plays! whoa!')
            else:
                print(f'{len(scores)} plays: ' + ', '.join(f"{w} {s}" for s, w in scores))
                print(f'{len(cand)} best candidates: ' + ', '.join(f'{w} {s}' for s, w in cand))
                win = random.choice([c for c in cand if len(c[1]) <= winlen and c[0] == win[0]])
                print(f'you should play {win[1]} horizontally on columns {column}-{column+len(win[1])-1} for {win[0]*2} points (double word score!)')
            print(f'this genius move took {(end-start)*1000:.2f}ms to come up with\n')
        if runs == 'm' or run == runs: break

    if runs != 'm' and runs > 1: print(f'average decision time over all runs was {(total_time/run)*1000:.2f}ms')
