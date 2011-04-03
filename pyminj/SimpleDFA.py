#!/usr/bin/env python

'''
@package PyMinJ
@class SimpleDFA
@brief The simple DFA class is built to emulate the basic functionality of a well-defined
       discrete finite automata based on input from a file
@note This class represents a loosely defined DFA in which any unknown transition will lead to a trapping final state
      denoted by None (in this way it acts somewhat like an NFA, but does not allow lambda transitions)
@note Transitions between states are not limited to individual chars, are matched as regular expressions
@author Stephen Young (st_youn@encs.concordia.ca)
'''

import re, fileinput, sys

class SimpleDFA:
    '''
    A simplistic implementation of discrete finite automata
    with focus on usage in a compilation scanner component
    '''

    CurrState = 0               # The current active state in the machine
    TransitionTable = {}        # The available transitions in the system
    StateTransitions = {}       # The available transitions from a given state
    FinalStates = []            # States considered final
    States = {}                 # Enumeration of states as string values


    def AddFinalState(self, state):
        '''Adds to the list of defined "accept" states'''
        if not state in self.FinalStates:
            self.FinalStates.append(state)

    def AddTransition(self, start_state, pattern, end_state):
        '''Adds another transition to the DFA and populates the alphabet'''
        if not start_state is None:
            self.TransitionTable[(start_state,pattern)] = end_state
            try:
                self.StateTransitions[start_state].append(pattern)
            except KeyError:
                self.StateTransitions[start_state] = [pattern]
        else:
            raise Exception("Start state cannot be none")

    def Advance(self, char):
        '''Uses the transition table to advance the DFA'''
        transition = False
        try:
            # Check to se if the pattern is available
            if self.__checkpattern(char):
                # If a match is found, transition to the match
                self.CurrState = self.TransitionTable[(self.CurrState,self.cpattern)]
                transition = True
                self.cpattern = None
            # If no transition is made, raise an exception and go to a trap state
            if not transition:
                raise Exception("No state transition available")
        except:
            # Trap until rewound
            self.CurrState = None
        return self.CurrState

    def __checkpattern(self,char):
        '''Checks to see if there is a pattern for the current state to match char'''
        # Ensure transitions exist for a given state
        if self.CurrState in self.StateTransitions:
            # Loop through the available patterns for the current state
            for pattern in self.StateTransitions[self.CurrState]:
                # Test to see if the character matches the pattern
                if re.match(pattern,char):
                    self.cpattern = pattern
                    return True
        # Return false if nothing was matched
        return False

    def Next(self,char):
        '''Returns true if the next character is still part of the token'''
        return self.__checkpattern(char)

    def State(self):
        '''Returns the current state, the enumerated constant value'''
        for name,id in self.States.iteritems():
            if int(id) == self.CurrState:
                return name
        return None

    def StateNum(self):
        '''Returns the integer value of the current state'''
        return self.CurrState

    def Check(self):
        '''Checks if we are in an accept state'''
        return self.CurrState in self.FinalStates

    def Reset(self):
        '''Resets the DFA to the starting state'''
        self.CurrState = 0

    def AddState(self,id,name):
        '''Adds another state to the automata'''
        self.States["<%s>" % name] = id

    def DenumerateStates(self,string):
        '''Translates all enumerated states into their numeric values in string'''
        for key,state in self.States.iteritems():
            string = re.sub(key,state,string)
        return string

    def Load(self,file):
        '''Loads and parses .dfa configuration file'''
        # Compile our regular expressions
        re_accept = r"^Accept:\W*([\d,]+)$"
        re_transitions = r"^Transitions:$"
        re_transition = r"(\d+),(.+?)[ ]+->[ ]+(\d+)"
        re_states =r"^States:$"
        re_state = r"^(\d+):\W*([a-zA-Z0-9_]*)$"

        transitions = False
        states = False
        # Basic DFA configuration file parser
        for line in fileinput.input([file]):
            # Remove comments
            line = line.strip()
            index = line.find('#')
            if index >= 0: line = line[:index].strip()
            # Ignore empty lines
            if len(line) > 0:
                # Populate transition rules
                if transitions:
                    # replace state names with state ids
                    line = self.DenumerateStates(line)
                    transition = re.match(re_transition,line)
                    if transition:
                        t = transition.groups()
                        self.AddTransition(int(t[0]),t[1],int(t[2]))
                # Populate state name rules
                elif states:
                    state = re.match(re_state,line)
                    if state:
                        self.AddState(state.group(1),state.group(2))
                # Check for accept states
                test_accept = re.match(re_accept,line)
                if test_accept:
                    for val in ''.join([g for g in test_accept.groups() if g != None]).split(','):
                        self.AddFinalState(int(val))
                # Check for transitions block
                elif re.match(re_transitions,line):
                    transitions = True
                # Check for states block
                elif re.match(re_states,line):
                    states = True




