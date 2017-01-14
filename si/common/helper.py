import typing

import si


def get_card_family_from_siid(
    siid: typing.Union[str, int]
  ) -> si.CardFamily:
  """
  Return the si.CardFamily representation for the given SIID
  """
  # References:
  # Helper.cs 9e291aa (#L692-L733)
  return si.CardFamily[get_card_type_from_siid(siid).name]


def get_card_type_from_siid(
    siid: typing.Union[str, int]
  ) -> si.CardType:
  """
  Return the si.CardFamily representation for the given SIID
  """
  # References:
  # Helper.cs 9e291aa (#L735-L816)
  try:
    siid = int(siid)
  except ValueError:
    return si.CardType.NotSet
  if (1 <= siid <= 65000):
    return si.CardType.Card5
  elif (200001 <= siid <= 265000):
    return si.CardType.Card5
  elif (300001 <= siid <= 365000):
    return si.CardType.Card5
  elif (400001 <= siid <= 465000):
    return si.CardType.Card5
  elif (500000 <= siid <= 999999):
    return si.CardType.Card6
  elif (1000000 <= siid <= 1999999):
    return si.CardType.Card9
  elif (2000000 <= siid <= 2799999):
    return si.CardType.Card8
  elif (2800000 <= siid <= 2999999):
    return si.CardType.ComCardUp
  elif (3000000 <= siid <= 3999999):
    return si.CardType.Card5
  elif (4000000 <= siid <= 4999999):
    return si.CardType.PCard
  elif (5373953 <= siid <= 5438952):
    return si.CardType.Card_5R
  elif (5570561 <= siid <= 5635560):
    return si.CardType.Card_5U
  elif (6000000 <= siid <= 6999999):
    return si.CardType.TCard
  elif (7000000 <= siid <= 7999999):
    return si.CardType.Card10
  elif (8000000 <= siid <= 8999999):
    return si.CardType.ActiveCard
  elif (9000000 <= siid <= 9999999):
    return si.CardType.Card11
  elif (14000000 <= siid <= 14999999):
    return si.CardType.FCard
  elif (16771680 <= siid <= 16777214):
    return si.CardType.Card6
  elif siid == 16777215:
    return si.CardType.ActiveCard
  else:
    return si.CardType.NotSet
