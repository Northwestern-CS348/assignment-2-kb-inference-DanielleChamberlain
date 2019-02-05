import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_rm_rule(self, r):
        for r in self.rules:
            if r.supported_by == [] and not r.asserted:
                for f1 in r.supports_facts:
                    g = f1.supported_by
                    for sup in g:
                        if sup[1] == r:
                            sup[0].supports_facts.remove(f1)
                            f1.supported_by.remove(sup)
                            if not f1.asserted:
                                self.kb_retract(f1)
                    for r1 in r.supports_rules:
                        g = r1.supported_by
                        for sup in g:
                            if sup[1] == r:
                                sup[0].supports_rules.remove(r1)
                                r1.supported_by.remove(sup)
                                if r1.supported_by == [] and not r1.asserted:
                                    self.kb_rm_rule(r1)
                    self.rules.remove(r)

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        print("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        if isinstance(fact_or_rule, Fact):
            for f in self.facts:
                if fact_or_rule.statement == f.statement:
                    f.asserted = False
                    if f.supported_by == []:
                        for f1 in f.supports_facts:
                            #print(f1.statement)
                            g = f1.supported_by
                            for sup in g:
                                if sup[0] == f:
                                    sup[1].supports_facts.remove(f1)
                                    f1.supported_by.remove(sup)
                                    if not f1.asserted:
                                        self.kb_retract(f1)
                        for r1 in f.supports_rules:
                            #print(r1.rhs)
                            g = r1.supported_by
                            for sup in g:
                                if sup[0] == f:
                                    sup[1].supports_rules.remove(r1)
                                    r1.supported_by.remove(sup)
                                    if r1.supported_by == [] and not r1.asserted:
                                        self.kb_rm_rule(r1)
                        self.facts.remove(f)

class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        binds = match(rule.lhs[0], fact.statement)
        if(binds):
            t = instantiate(rule.rhs, binds)
            rl = False
            for tr in t.terms:
                if is_var(tr):
                    rl = True
                    break
            if rl:
                #print('infer new rule')
                new_rule = Rule([[], t])
                new_rule.asserted = False
                new_rule.supported_by.append([fact, rule])
                for sta in rule.lhs:
                    if sta != rule.lhs[0]:
                        new_rule.lhs.append(instantiate(sta, binds))
                kb.kb_add(new_rule)
                fact.supports_rules.append(new_rule)
                rule.supports_rules.append(new_rule)
            else:
                #print('infer new fact')
                new_fact = Fact(t)
                new_fact.asserted = False
                new_fact.supported_by.append([fact, rule])
                kb.kb_add(new_fact)
                fact.supports_facts.append(new_fact)
                rule.supports_facts.append(new_fact)









