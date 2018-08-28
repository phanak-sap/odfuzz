"""This module contains functions for patching property objects generated by pyodata library"""

import random
import logging

from pyodata.v2.model import VariableDeclaration
from odfuzz.generators import RandomGenerator
from odfuzz.mutators import StringMutator, NumberMutator, GuidMutator, BooleanMutator, DecimalMutator, DateTimeMutator
from odfuzz.constants import BOOLEAN_OPERATORS, EXPRESSION_OPERATORS, INTERVAL_OPERATORS

MAX_STRING_LENGTH = 100


def patch_proprties(entity_set):
    for proprty in entity_set.entity_type.proprties():
        patch_proprty_max_length(proprty)
        patch_proprty_generator(proprty)
        patch_proprty_mutator(proprty)
        patch_proprty_operator(proprty)


def patch_proprty_max_length(proprty):
    proprty_type = proprty.typ.name
    if proprty_type == 'Edm.String':
        proprty.max_string_length = max_string_length(proprty.max_length)


def max_string_length(max_length):
    if not max_length or max_length == VariableDeclaration.MAXIMUM_LENGTH:
        return MAX_STRING_LENGTH
    return max_length


def patch_proprty_generator(proprty):
    proprty_type = proprty.typ.name
    if proprty_type == 'Edm.String':
        proprty.generate = RandomGenerator.edm_string.__get__(proprty, None)
    elif proprty_type == 'Edm.DateTime':
        proprty.generate = RandomGenerator.edm_datetime
    elif proprty_type == 'Edm.Boolean':
        proprty.generate = RandomGenerator.edm_boolean
    elif proprty_type == 'Edm.Byte':
        proprty.generate = RandomGenerator.edm_byte
    elif proprty_type == 'Edm.SByte':
        proprty.generate = RandomGenerator.edm_sbyte
    elif proprty_type == 'Edm.Single':
        proprty.generate = RandomGenerator.edm_single
    elif proprty_type == 'Edm.Guid':
        proprty.generate = RandomGenerator.edm_guid
    elif proprty_type == 'Edm.Decimal':
        proprty.generate = RandomGenerator.edm_decimal.__get__(proprty, None)
    elif proprty_type == 'Edm.DateTimeOffset':
        proprty.generate = RandomGenerator.edm_datetimeoffset
    elif proprty_type == 'Edm.Time':
        proprty.generate = RandomGenerator.edm_time
    elif proprty_type == 'Edm.Binary':
        proprty.generate = RandomGenerator.edm_binary
    elif proprty_type.startswith('Edm.Int'):
        if proprty_type.endswith('16'):
            proprty.generate = RandomGenerator.edm_int16
        elif proprty_type.endswith('32'):
            proprty.generate = RandomGenerator.edm_int32
        elif proprty_type.endswith('64'):
            proprty.generate = RandomGenerator.edm_int64
        else:
            logging.error('Property type {} is not supported by generator yet'.format(proprty_type))
    else:
        logging.error('Property type {} is not supported by generator yet'.format(proprty_type))


def patch_proprty_mutator(proprty):
    proprty_type = proprty.typ.name
    if proprty_type == 'Edm.String':
        set_mutator_methods(proprty, StringMutator)
        proprty.mutate = get_string_mutator_method.__get__(proprty, None)
    elif proprty_type.startswith('Edm.Int'):
        set_mutator_methods(proprty, NumberMutator)
        proprty.mutate = get_num_mutator_method.__get__(proprty, None)
    elif proprty_type == 'Edm.Guid':
        proprty.mutate = GuidMutator.replace_char
    elif proprty_type == 'Edm.Boolean':
        proprty.mutate = BooleanMutator.flip_value
    elif proprty_type == 'Edm.Decimal':
        # TODO
        proprty.mutate = lambda value: value
    elif proprty_type == 'Edm.DateTime':
         # TODO
        proprty.mutate = lambda value: value
    else:
        proprty.mutate = lambda value: value
        logging.error('Property type {} is not supported by mutator yet'.format(proprty_type))


def set_mutator_methods(proprty, mutators_class):
    func_mutators = [{func_name: func_obj} for func_name, func_obj
                     in mutators_class.__dict__.items() if not func_name.startswith('_')]
    for mutator in func_mutators:
        for name, obj in mutator.items():
            setattr(proprty, name, obj.__get__(proprty, None))


def get_string_mutator_method(self, value):
    func_name = random.choice([func_name for func_name in StringMutator.__dict__ if not func_name.startswith('_')])
    mutated_value = getattr(self, func_name)(self, value)
    return mutated_value


def get_num_mutator_method(self, value):
    func_name = random.choice([func_name for func_name in NumberMutator.__dict__ if not func_name.startswith('_')])
    mutated_value = getattr(self, func_name)(self, value)
    return mutated_value


def patch_proprty_operator(proprty):
    proprty_type = proprty.typ.name
    if proprty.filter_restriction in ('single-value', 'multi-value'):
        proprty.operators = Operators({'eq': 1.0})
    elif proprty.filter_restriction == 'interval':
        proprty.operators = IntervalOperators((INTERVAL_OPERATORS, {'eq': 1.0}))
    elif proprty_type == 'Edm.Boolean':
        proprty.operators = Operators(BOOLEAN_OPERATORS)
    else:
        proprty.operators = Operators(EXPRESSION_OPERATORS)


class Operators(object):
    def __init__(self, operators):
        self._operators = operators

    def get_all(self):
        return self._operators.items()


class IntervalOperators(object):
    def __init__(self, operators_groups):
        self._operators_groups = operators_groups

    def get_all(self):
        operators = random.choice(self._operators_groups)
        return operators.items()
