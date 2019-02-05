import unittest
import read, copy
from logical_classes import *
from student_code import KnowledgeBase

class KBTest(unittest.TestCase):

    def setUp(self):
        # Assert starter facts
        file = 'statements_kb4.txt'
        self.data = read.read_tokenize(file)
        data = read.read_tokenize(file)
        self.KB = KnowledgeBase([], [])
        for item in data:
            if isinstance(item, Fact) or isinstance(item, Rule):
                self.KB.kb_assert(item)
        
    def test1(self):
        # Did the student code contain syntax errors, AttributeError, etc.
        ask1 = read.parse_input("fact: (motherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : bing")

    def test2(self):
        # Can fc_infer actually infer
        ask1 = read.parse_input("fact: (grandmotherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : felix")
        self.assertEqual(str(answer[1]), "?X : chen")

    def test3(self):
        # Does retract actually retract things 
        r1 = read.parse_input("fact: (motherof ada bing)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)
        ask1 = read.parse_input("fact: (grandmotherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(len(answer), 1)
        self.assertEqual(str(answer[0]), "?X : felix")

    def test4(self):
        # makes sure retract does not retract supported fact
        ask1 = read.parse_input("fact: (grandmotherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : felix")
        self.assertEqual(str(answer[1]), "?X : chen")

        r1 = read.parse_input("fact: (grandmotherof ada chen)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)

        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : felix")
        self.assertEqual(str(answer[1]), "?X : chen")
        
    def test5(self):
        # makes sure retract does not deal with rules
        ask1 = read.parse_input("fact: (parentof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : bing")
        r1 = read.parse_input("rule: ((motherof ?x ?y)) -> (parentof ?x ?y)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : bing")

    def test6(self):
        """this student generated test ensures retract only removes facts and rules that are supported by
        1 or less fact-rule pairs
        """
        r1 = read.parse_input("fact: (dresslike profHammond TonyStark)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)
        ask1 = read.parse_input("fact: (isliterally ?X TonyStark)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : profHammond")
        ask2 = read.parse_input("fact: (resembles profHammond ?Y)")
        print(' Asking if', ask2)
        answer = self.KB.kb_ask(ask2)
        self.assertFalse(answer)

    def test7(self):
        """this student generated test ensures retracting the 2nd fact in the lhs of a rule
        successfully retracts the final inferred fact but re-assertion re-infers the fact
        """
        r1 = read.parse_input("fact: (lookslike profHammond TonyStark)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)
        ask1 = read.parse_input("fact: (resembles profHammond ?Y)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertFalse(answer)
        a1 = read.parse_input("fact: (lookslike profHammond TonyStark)")
        print(' Reasserting', a1)
        self.KB.kb_assert(a1)
        ask2 = read.parse_input("fact: (resembles profHammond ?Y)")
        print(' Asking if', ask2)
        answer = self.KB.kb_ask(ask2)
        self.assertEqual(str(answer[0]), "?Y : TonyStark")

    def test8(self):
        """this student generated test ensures retracting a fact that supports inferences 2 links away
        also retracts all facts down that chain
        """
        r1 = read.parse_input("fact: (techgenius profHammond)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)
        r2 = read.parse_input("fact: (talkslike profHammond TonyStark)")
        print(' Retracting', r2)
        self.KB.kb_retract(r2)
        ask1 = read.parse_input("fact: (isliterally ?X TonyStark)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertFalse(answer)
        ask2 = read.parse_input("fact: (IronMan ?X)")
        print(' Asking if', ask2)
        answer = self.KB.kb_ask(ask2)
        self.assertFalse(answer)
        ask3 = read.parse_input("fact: (Avenger ?X)")
        print(' Asking if', ask3)
        answer = self.KB.kb_ask(ask3)
        self.assertFalse(answer)

    def test9(self):
        """this student generated test ensures retracting a fact that supports two or more facts or rules
        successfully retracts all inferred facts and rules
        """
        r1 = read.parse_input("fact: (techgenius profHammond)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)
        ask1 = read.parse_input("fact: (employable ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertFalse(answer)
        ask2 = read.parse_input("fact: (smart ?X)")
        print(' Asking if', ask2)
        answer = self.KB.kb_ask(ask2)
        self.assertFalse(answer)

    def test10(self):
        """this student generated test ensures the inference engine is working at a basic level"""
        ask1 = read.parse_input("fact: (Avenger ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : profHammond")
        ask2 = read.parse_input("fact: (smart ?X)")
        print(' Asking if', ask2)
        answer = self.KB.kb_ask(ask2)
        self.assertEqual(str(answer[0]), "?X : profHammond")
        ask3 = read.parse_input("fact: (employable ?X)")
        print(' Asking if', ask3)
        answer = self.KB.kb_ask(ask3)
        self.assertEqual(str(answer[0]), "?X : profHammond")


def pprint_justification(answer):
    """Pretty prints (hence pprint) justifications for the answer.
    """
    if not answer: print('Answer is False, no justification')
    else:
        print('\nJustification:')
        for i in range(0,len(answer.list_of_bindings)):
            # print bindings
            print(answer.list_of_bindings[i][0])
            # print justifications
            for fact_rule in answer.list_of_bindings[i][1]:
                pprint_support(fact_rule,0)
        print

def pprint_support(fact_rule, indent):
    """Recursive pretty printer helper to nicely indent
    """
    if fact_rule:
        print(' '*indent, "Support for")

        if isinstance(fact_rule, Fact):
            print(fact_rule.statement)
        else:
            print(fact_rule.lhs, "->", fact_rule.rhs)

        if fact_rule.supported_by:
            for pair in fact_rule.supported_by:
                print(' '*(indent+1), "support option")
                for next in pair:
                    pprint_support(next, indent+2)



if __name__ == '__main__':
    unittest.main()
