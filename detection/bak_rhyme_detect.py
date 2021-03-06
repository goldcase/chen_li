#!/usr/bin/python

#############################################
# TODO: add error detection and error messages
# TODO: add better perfect rhyme detection <-- DONE???
# TODO: add scoring
# TODO: add support for more than 1 text file
# TODO: add detection of more rhymes <-- DONE
# TODO: lots of other shit basically <-- Well... yeah
# TODO: separate methods from testing <-- what's dat mean <- I'll take care of this
# TODO: change methods to use already transcribed strings (you know, speed probably)
# TODO: multi syllabic rhymes <-- DONE
# TODO: scrape AZ Lyrics and scrub <-- basics are done
# TODO: denstiy plot of rhymes
# TODO: pick out a nonwestern for us to take spring semester
# TODO: nice todo, also scrub rhymes for punctuation because CMU dict is fucking stupid <-- DONE
# TODO: measure *based on syllables* <-- whats dat mean <- nvm
#############################################

#############################################
# NEW TODOS
# TODO: handle words not in cmudict <- this is hard
# TODO: make big wrap method that does all rhyme detection
# TODO: error handling with web scraping (ie no results or first result is not right one)
# TODO: put scraping and processing together
# TODO: find_matching_phonemes needs some love or to be deleted
#############################################

import sys
import nltk
import pprint
from nltk.corpus import cmudict
from collections import defaultdict, OrderedDict

###########################
# BEGIN: GLOBAL VARIABLES #
###########################

# Sample rhymes in the form of a string, or a list of strings
# More sample rhymes are located in the text files
# Import text files by using command line arguments

# Lose Yourself - Eminem
LOSE_YOURSELF = ["His palms are sweaty knees weak arms are heavy",
                 "There vomit on his sweater already moms spaghetti",
                 "He nervous but on the surface he looks calm and ready to drop bombs",
                 "But he keeps on forgetting what he wrote down",
                 "The whole crowd goes so loud",
                 "He opens his mouth but the words wont come out"]

PERFECT_RHYME = ["This is a perfect rhyme", 
                 "bitches split on a dime"]

BREAK_PERFECT_RHYME = ["This is NOT a perfect rhyme and with some luck",
                       "The method will know this and not be a dick"]

BREAK_PERFECT_RHYME_YET_AGAIN = ["Nice try Johnny boy your effort was good",
                                "but I have a leg up or at least a foot"]

ALLITERATION_RHYME1 = ["Look I was gonna go easy on you and not to hurt your feelings",
                      "But I'm only going to get this one chance"]

ALLITERATION_RHYME2 = ["Big big booty what you got a big booty"]

ASSONANCE_RHYME = ["Maybe bake cake Jay C rapper star"]

SAMPLE_TEXT = "Mackerel bat from hell"

SAMPLE_TEXT2 = "Wow Jay C is asking for it, gonna punch him in a little bit" # that doesn't rhyme, fish can't rap <<< happy?

RAP_GOD = ["I'm beginning to feel like a Rap God, Rap God",
           "All my people from the front to the back nod, back nod"]

HOL_UP = ["I wrote this record while thirty thousand feet in the air",
          "Stewardess complimenting me on my happy hair",
          "If I can fuck her in front of all of these passengers",
          "They'll probably think I'm a terrorist eat my asparagus",
          "Then I'm asking her thoughts of a young bigger fast money and freedom",
          "A crash dummy for dollars I know you dying to meet them",
          "I'll holly die in a minute just bury me",
          "With twenty bitches twenty million and a Cop town fitted"]

GET_RID_OF_DAT_PUNCT = "This'll, have: a; (ton) of _pointless -punctuation"

transcr = cmudict.dict()

vowels = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']

#########################
# END: GLOBAL VARIABLES #
#########################

#########################################
# BEGIN: Functions that act like macros #
#########################################

def line_break():
    print("\n")

def horiz_line():
    print("==============================")

#######################################
# END: Functions that act like macros #
#######################################

# read_and_scrub_text_file(i)
# Description: reads the text file and returns a scrubbed list of strings ready to transcribe
# param      : i, an integer (>= 1) referring to which argument to open and read
# return     : a list of scrubbed strings

def read_and_scrub_text_file(i):
    file_1 = open(sys.argv[1])        # Open text file at first argument of command line in *read* mode
    file1_lines = file_1.readlines()  # returns list of strings with new line characters at the end
    lines_scrubbed = []               # initialize empty list for return value

    for s in file1_lines:             # loop through each line read in from the text file
        lines_scrubbed.append(s[:-1]) # purge the new line characters so now we have a clean list of strings to transcribe
    file_1.close()                    # close the file to free up resources

    return lines_scrubbed

# scrub_punct(lines)
# Description: takes a line and scrubs it of all punctuation
# param      : a string
# return     : a punctuation scrubbed string (oooo, ahhhhh)

def scrub_punct(lines):
    line = lines.split()                        # list of words in line
    temp_line = []                              # scrubbed line
    for j in line:                              # go word by word
        if j.isalpha():                         # no punctuation to remove in this word in the line
            temp_line.append(j)                 # add normaly
        else:                                   # there is punctuation to remove
            temp_word = []
            for k in j:                         # go letter by letter
                if k.isalpha() or k == "'":     # this is not a punctuation character
                    temp_word.append(k)         # add to the currnet scrubbed word
            temp_line.append("".join(temp_word))
    return (" ".join(temp_line))                # add to list of scrubbed lines

# transcribe_string(string)
# Description: transcribes a string into its phonemes and prints the result out.
# param      : string str to transcribe
# return     : list of lists of phonemes

def transcribe_string(string):
    results = [transcr[w][0] for w in string.lower().split()]  # transcribes the sample string given to the CMU Dictionary.

    return results

# transcribe_list(l)
# Description: converts a list of strings into a list of list of lists of phonemes per word
# param      : list of strings
# return     : transcribed list of list of lists of phonemes

def transcribe_list(l):
    list_transcription = []                             # initialize return value to empty list
    for w in l:                                         # iterate through each string in argument
        list_transcription.append(transcribe_string(w)) # transcribe string and append list of phonemes to return value

    return list_transcription

# detect_perfect_rhyme_two_lines(a, b)
# Description: detects a perfect rhyme (definition below) between 2 passed strings
#            : perfect rhyme: a rhyme in which the endings of words sound exactly the same
#            : http://genius.com/posts/24-Rap-genius-university-rhyme-types
# param      : *un-transcribed* string 1, *un-transcribed* string 2
# return     : True if perfect rhyme detected, False if not

def detect_perfect_rhyme_two_lines(a, b):
    a_syl = syllable_string(a) # Transcribe string a into its syllables
    b_syl = syllable_string(b) # Transcribe string b into its syllables 

    print a_syl
    print b_syl

    a_last = a_syl[-1][0]                                               # get last word of each line
    b_last = b_syl[-1][0]

    print a_last
    print b_last

    a_index = len(a_last)-1                                             # index of last phoneme
    b_index = len(b_last)-1
    while min(a_index, b_index) >= 0:                                   # while the smaller index is greater than 0
        if a_last[a_index] != b_last[b_index]:                          # if phonemes don't match, not a perfect rhyme
            break
        if is_vowel(a_last[a_index]) and a_index < len(a_last):         # if we hit a vowel and this vowel is not the last phoneme in the word    
            return True                                                 # ^ this prevents words like gamma and camera from being considered perfect rhyme
        a_index-=1
        b_index-=1
    return False

# detect_alliteration(a)
# Description: detects alliterations within ONE line
# param      : *un-transcribed* string a
# return     : a list of tuples, first element is phoneme, second is the number of times it appears, third is index in line where assonance begins
#            : lenght of this list gives you total number of alliterations in line

def detect_alliteration(a):
    a_transcr = transcribe_string(a)                           # Transcribe string a into its pronunciations
    ret = []
    x = 0                                                      # go through words
    while x < len(a_transcr):
        num_times = 0
        y = 1
        stop = False
        while not(stop) and y < (len(a_transcr) - x):
            stop = True
            if a_transcr[x][0] == a_transcr[x + y][0]:
                num_times += 1
                stop = False                                   # keep searching forwards
                y += 1                                         # look one word further
                                                               # figure out how to check 1-2 more words in advnace
        if num_times > 0:
            ret.append((a_transcr[x][0], num_times, x))        # add this alliteration to the list
            x = x + y + 1                                      # start searching for more alliterations after this one ends to avoid double counting
        else:
            x += 1
    return ret

# detect_assonance_in_line(a)
# Description: detects assonance within ONE line
# param      : *un-transcribed* string a
# return     : a list of tuples, first element is phoneme, second is the number of times it appears, third is index in line where assonance begins
#            : lenght of this list gives you total number of assonance in line

def detect_assonance_in_line(a):
    a_transcr = transcribe_string(a)                 # Transcribe string a into its pronunciations
    ret = []
    x = 0                                            # go through words
    while x < len(a_transcr):
        vowels = []
        newX = x + 1
        for z in a_transcr[x]:                       # find the vowels in the word
            if is_vowel(z):
                vowels.append(z)
        for w in vowels:                             # check each vowel to see if there is assonance within the line
            num_times = 0
            y = 1
            stop = False
            while not(stop) and y < (len(a_transcr) - x):
                stop = True
                if w in a_transcr[x + y]:
                    num_times += 1
                    stop = False                     # keep searching forwards
                    y += 1                           # look one word further
                                                     # figure out how to check 1-2 more words in advnace
            if num_times > 0:
                ret.append((w, num_times, x))        # add this assonance to the list
                if x + y + 1 > newX:
                    newX = x + y + 1                 # start searching for more assonance after this one ends to avoid double counting
        x = newX
    return ret

# is_vowel(phoneme)
# Description: determines if a phoneme is a vowel sound
# param      : phoneme string
# return     : true if phoneme is a vowel sound, else false

def is_vowel(phoneme):
    if phoneme[-1].isdigit:
        phoneme = phoneme[:-1]
    if phoneme in vowels:
        return True
    else:
        return False

# syllable_count(word)
# Description: counts the number of syllables in a transcribed word
#            : this only works for a single word, not a line
# param      : list of phonemes (a transcribed string word)
# return     : integer number of syllables

def syllable_count(phonemes):
    ret = 0
    for x in phonemes:
        for y in x:
            if y[-1].isdigit():         # if the phoneme ends in a number, marks a syllable
                ret+=1
    return ret

# syllable_word(phonemes)
# Description: returns a list with each element representing the phonemes that make up a syllable in that word
# param      : list of phonemes (a transcribed string word)
# return     : list of lists of phonemes; each element of the main list constitutes a syllable

def syllable_word(phonemes):
    ret = []
    count = 1
    for x in phonemes:                                                # iterate through phonemes for that word
        temp = []
        for y in x: 
            temp.append(y) 
            if y[-1].isdigit():                                       # if the phoneme ends in a digit, then we know it's the end of that syllable 
                ret.append(temp)
                temp = []
        if (len(phonemes) == count) and not(len(temp) == 0):          # tack on last few phonemes if there are any left
            ret[-1] += temp
        count += 1
    return ret

# syllable_string(l)
# Description: we want a list of syllables for the string you enter
# param      : string, not already transcribed
# return     : list of list of syllables by word

def syllable_string(s):
    ret = []
    l = s.split(' ')

    for w in l:                                        # for every word in the list
       ret.append(syllable_word(transcribe_string(w))) # syllable-ize that word

    return ret

# syllable_string_no_word_boundaries(s)
# Description: we want a list of syllables for the string you enter, without word divisions
# param      : string, not already transcribed
# return     : list of syllables
#            : I now realize how stupid this method was

def syllable_string_no_word_boundaries(s):
    ret = []
    l = s.split(' ') # split s into constituent words

    for w in l: # for every word in the list
        werd = syllable_word(transcribe_string(w))
        for syl in werd:
            ret += syl

    return ret

# syllable_total(l)
# Description: Stupid Method
# param      : *not already trancribed* list of strings
# return     : big list of syllables per line (NOT BY WORD, as in: unseparated)

def syllable_total(l):
    ret = []
    for s in l:
        syl_str = syllable_string(s)
        temp = []
        for line in syl_str:
            temp += line 
        ret.append(temp)

    return ret

# find_matching_phonemes(a, b)
# Description: finds matching phonemes between a, b, and returns a list of booleans corresponding with indices and whether they match
#            : this is going to be really hacky
# param      : list of phonemes a, list of phonemes b
# return     : list of booleans

def find_matching_phonemes(a, b):
    # maybe i will fix this method later
    return

# phoneme_freq(l)
# Description: creates a frequency dict of phonemes in a line and sorts by frequency of appearance
# param      : transcribed line to scanalyze (I am a born rapper)
# return     : sorted frequency dict by number of phonemes (type OrderedDict)
# note       : in hindsight this might be totally unnecessary <-- i dont think it is since your vowel freq and allit freq do this for the phonemes we care about

def phoneme_freq(l):
    d = defaultdict(int)                                      # default dict with value int

    for w in l:                                               # for every word in the list
        for p in w:                                           # and every phoneme in the word
            d[p] += 1                                         # add it/increment it in the dict

    od = OrderedDict(sorted(d.items(), key = lambda t: t[1])) # then add it to an OrderedDict sorted by value
    
    return od

# vowel_freq(l), originally named ass_freq(l) <-- haha, not everything has to do with your ass johnny
# Description: shows the most frequent vowels in that line
# param      : transcribed list of phonemes (only one string)
# return     : OrderedDict of vowel phonemes to their frequency of appearance

def vowel_freq(l):
    d = defaultdict(int)                                                      # create defaultdict

    for w in l:                                                               # for every word in the list of lists of phonemes
        for p in w:                                                           # for every list of phonemes
            if is_vowel(p):                                                   # if that is a vowel
                d[p] += 1                                                     # increment its count in the dictionary

    od = OrderedDict(sorted(d.items(), key = lambda t: t[1], reverse = True)) # add these in descending order to the OrderedDict

    return od

# allit_freq(l)
# Description: Which alliterations are most frequent?
# param      : transcribed list of phonemes (only one string)
# return     : OrderedDict of alliteration phonemes to their frequency of appearance in *descending order*

def allit_freq(l):
    d = defaultdict(int)                                                      # create defaultdict

    for w in l:                                                               # for every list in the list of phonemes
        d[w[0]] += 1                                                          # add its first sound to the default dictionary

    od = OrderedDict(sorted(d.items(), key = lambda t: t[1], reverse = True)) # add these in descending order to the OrderedDict

    return od

# extract_vowels(l)
# Description: extracts vowels from a list of phonemes
# param      : list of phonemes to extract vowels from 
# return     :  sequence of vowels from the passed in list of phonemes

def extract_vowels(l):
    ret = []

    for x in l        :   # for every phoneme in the list
        if is_vowel(x):   # if it belongs to the list of vowels
            ret.append(x) # add that to the return list
    
    return ret

# multi_sequence(a, b)
# Description: What is the longest ending multisyllabic rhyme between 2 lines?
# param      : untranscribed string a, b
# return     : longest matching sequence between the two

def multi_sequence(a, b):
    syll_a = syllable_string_no_word_boundaries(a) # i realized how stupid this was after i wrote it... don't comment :)
    syll_b = syllable_string_no_word_boundaries(b)

    vowels_a = extract_vowels(syll_a)
    vowels_b = extract_vowels(syll_b)

    sequence = []

    for i in range(-1, -1 * min(len(a), len(b)), -1): # loop from the end of each array in steps of -1 <- very clever <- xie xie
        if vowels_a[i] == vowels_b[i]:
            sequence.insert(0, vowels_a[i])
        else:
            break

    return sequence

#######################
# BEGIN: TEST SECTION #
#######################

#####################
# BEGIN SCRUB TESTS #
#####################

horiz_line()
print("BEGIN TESTS")
horiz_line()

if (len(sys.argv) > 1):
    line_break()
    print("ARGUMENTS DETECTED")
    print("TEST COMMAND LINE:")
    print("Argument List " + str(sys.argv))
    print("Number of arguments: " + str(len(sys.argv)))
    print("SCRUBBED LINES:")
    print(read_and_scrub_text_file(1))

line_break()
print("TESTING: transcribe_string(SAMPLE_TEXT)")
sample_transcr = transcribe_string(SAMPLE_TEXT) # test that transcribe_string function works
print(sample_transcr)                           # Prints out phonemes for "Mackerel bat from hell"

line_break()
print("TESTING: transcribe_list(PERFECT_RHYME)")
perfect_transcr = transcribe_list(PERFECT_RHYME) # test that transcribe_list function works correctly
print(perfect_transcr)                           # output should match what we have below
print("WHAT ARE THE LENGTHS OF EACH TRANSCRIPTION")
arr = [0,0]
for i in range(len(perfect_transcr)):
    for t in perfect_transcr[i]:
        for s in t:
            arr[i] += 1
print(arr)


line_break()
print("TEST FOR MATCH: transcribe_list(PERFECT_RHYME)") # test for matching output
for s in PERFECT_RHYME:
    print(transcribe_string(s))                         # transcribe_list ouputs match! yay!

line_break()
print("TEST FOR PUNCTUATION SCRUBBING:")
print GET_RID_OF_DAT_PUNCT
print scrub_punct(GET_RID_OF_DAT_PUNCT)

###################
# END SCRUB TESTS #
###################

#########################
# BEGIN DETECTION TESTS #
#########################

line_break()
horiz_line()
print("Now comes the detection output:")
horiz_line()

line_break()
print("TEST FOR PERFECT RHYME:")                                          # test that perfect rhyme detection works
print(PERFECT_RHYME)                                                      # ['This is a perfect rhyme', 'bitches split on a dime']
print(transcribe_list(PERFECT_RHYME))
print(detect_perfect_rhyme_two_lines(PERFECT_RHYME[0], PERFECT_RHYME[1])) # Expected: True (yay!)

line_break()
print("TEST FOR PERFECT RHYME:")                                            # test that perfect rhyme doesnt give false positives
print(BREAK_PERFECT_RHYME)                                                  # 'This is NOT a perfect rhyme and with some luck', 'The method will know this and not be a dick']
print(detect_perfect_rhyme_two_lines(BREAK_PERFECT_RHYME[0], BREAK_PERFECT_RHYME[1])) # Expected: False (boo! :( )

line_break()
print("TEST FOR PERFECT RHYME:")                                                        # test that perfect rhyme doesnt give false positives
print(BREAK_PERFECT_RHYME_YET_AGAIN)                                                    # 'Nice try Johnny boy your effort was good', 'but I have a leg up or at least a foot']
print(detect_perfect_rhyme_two_lines(BREAK_PERFECT_RHYME_YET_AGAIN[0], BREAK_PERFECT_RHYME_YET_AGAIN[1])) # Expected: False (boo! :( )

line_break()
print("TEST FOR ALLITERATION RHYME:")
print(ALLITERATION_RHYME1)
print(detect_alliteration(ALLITERATION_RHYME1[0]))

line_break()
print(ALLITERATION_RHYME2)
print(detect_alliteration(ALLITERATION_RHYME2[0]))

line_break()
print("TEST FOR ASSONANCE RHYME WITHIN LINE:")
print(ASSONANCE_RHYME)
print(detect_assonance_in_line(ASSONANCE_RHYME[0]))

line_break()
print("TEST FOR MATCHING PHONEMES:")
print(find_matching_phonemes(transcribe_string(PERFECT_RHYME[0]), transcribe_string(PERFECT_RHYME[1])))

########################
# END DETECTION TESTS #
########################

#########################
# BEGIN SYLLABLE TESTS #
#########################

line_break()
horiz_line()
print("Jay C in the hiz-house testing dem syllables:")
horiz_line()

line_break()
print("TEST FOR SINGLE WORD:") # next test: mack-er-el
print("AMAZING")
print(syllable_count(transcribe_string("amazing")))
print(syllable_word(transcribe_string("amazing")))
print(transcribe_string("amazing"))

line_break()
print("TEST SYLLABLE_WORD METHOD:")
print "hello"
print syllable_word((transcribe_string("hello")))
print len(syllable_word((transcribe_string("hello"))))  # Expected: 2 yay!
line_break()
print "this"
print syllable_word((transcribe_string("this")))
print len(syllable_word((transcribe_string("this"))))  # Expected: 3 yay!
line_break()
print "bottle"
print syllable_word((transcribe_string("bottle")))
print len(syllable_word((transcribe_string("bottle"))))  # Expected: 2 yay!
line_break()
print "is"
print syllable_word((transcribe_string("is")))
print len(syllable_word((transcribe_string("is"))))  # Expected: 3 yay!
line_break()
print "wonderful"
print syllable_word((transcribe_string("wonderful")))
print len(syllable_word((transcribe_string("wonderful"))))  # Expected: 3 yay!
line_break()
print "clocks"
print syllable_word((transcribe_string("clocks")))
print len(syllable_word((transcribe_string("clocks"))))  # Expected: 1 yay!

line_break()
print("TEST SYLLABLE_STRING METHOD:")
print("hello this bottle is wonderful")
print(syllable_string("hello this bottle is wonderful"))

line_break()
print("TEST SYLLABLE TOTAL METHOD:")
pprint.pprint(LOSE_YOURSELF)
lose_yourself_total_syllables = syllable_total(LOSE_YOURSELF)
print(lose_yourself_total_syllables)

line_break()
print("FIND SYLLABLE COUNTS OF LOSE YOURSELF")
for x in lose_yourself_total_syllables:
    print(len(x))

line_break()
print("TEST SYLLABLE TOTAL METHOD, HOL UP:")
pprint.pprint(HOL_UP)
hol_up_total_syllables = syllable_total(HOL_UP)
print(hol_up_total_syllables)

line_break()
print("FIND SYLLABLE COUNT OF HOL UP")
for x in hol_up_total_syllables:
    print(len(x))

print("TEST SYLLABLE NO BOUNDARIES:")
pprint.pprint(SAMPLE_TEXT)
print(syllable_string_no_word_boundaries(SAMPLE_TEXT))

########################
# END SYLLABLE TESTS #
########################

####################
# BEGIN FREQ TESTS #
####################

line_break()
horiz_line()
print("Mack-lemore & Jay-C Collab on Frequency Methods, Ass & All")
horiz_line()

line_break()
print("TESTING VOWEL_FREQ")
print(SAMPLE_TEXT)
print(transcribe_string(SAMPLE_TEXT))
vowel_od_1 = vowel_freq(transcribe_string(SAMPLE_TEXT))
for k, v in vowel_od_1.items():
    print k, v

line_break()
print("TESTING VOWEL FREQ MORE SERIOUSLY")
print(LOSE_YOURSELF)
print(transcribe_list(LOSE_YOURSELF))
vowel_od_2 = []
for l in LOSE_YOURSELF:
    vowel_od_2.append(vowel_freq(transcribe_string(l)))

for x in vowel_od_2:
    print("\n")
    for k, v in x.items():
        print k, v

line_break()
print("TESTING ALLITERATION_FREQ")
print(ALLITERATION_RHYME1[0])
print(transcribe_string(ALLITERATION_RHYME1[0]))
allit_od_1 = allit_freq(transcribe_string(ALLITERATION_RHYME1[0]))
for k, v in allit_od_1.items():
    print k, v

##################
# END FREQ TESTS #
##################

#####################
# BEGIN MULTI TESTS #
#####################

horiz_line()
print("TESTING MULTISYLLABIC RHYMES BRACE YOUR ASSONANCE")
horiz_line()

line_break()
print(LOSE_YOURSELF[3])
print(LOSE_YOURSELF[4])
pprint.pprint(multi_sequence(LOSE_YOURSELF[3],LOSE_YOURSELF[4]))

if (len(sys.argv) > 1):
    multi_file_swag = []
    line_break()
    file_swag = read_and_scrub_text_file(1)
    for i in range(0, len(file_swag) - 1):
        temp = multi_sequence(file_swag[i], file_swag[i + 1])
        if len(temp) != 0:
            multi_file_swag.append(temp)
    pprint(multi_file_swag)
        
        
    
###################
# END MULTI TESTS #
###################

#####################
# END TEST SECTION #
#####################
