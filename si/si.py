from enum import IntEnum

# TODO: doscstrings; more info

class AirPlusRadioMode(IntEnum):
  # References:
  # SPORTident 9e291aa \AirPlusRadioMode.cs
  NotSetOrDisabled = 0
  SrRadioSendLast = 1
  SrRadioSendAll = 2
  SrRadioSendAllNew = 3


class AirPlusSpecialMode(IntEnum):
  # References:
  # SPORTident 9e291aa \AirPlusSpecialMode.cs
  NotSetOrDisabled = 0
  SiacBatteryTest = 123
  SiacSwitchOn = 124
  SiacSwitchOff = 125
  SiacRadioReadout = 127


class BeaconTimingMode(IntEnum):
  # References:
  # SPORTident 9e291aa \BeaconTimingMode.cs
  Unknown = -1
  TimingMode = 0
  PunchingMode = 1


class CardFamily(IntEnum):
  # References:
  # Helper.cs 9e291aa (#L692-L816)
  NotSet = 0
  Card5 = 0
  Card_5U = 0
  Card_5R = 0
  Card6 = 0
  Card9 = 1
  Card8 = 2
  ComCardUp = 2
  ComCardPro = 2
  ComCardAir = 2
  PCard = 4
  TCard = 6
  FCard = 14
  Card10 = 15
  ActiveCard = 15
  Card11 = 15


class CardType(IntEnum):
  # References:
  # SPORTident 9e291aa \CardType.cs
  NotSet = 0
  Card5 = 1
  Card6 = 2
  Card8 = 3
  Card9 = 4
  Card10 = 5
  Card11 = 6
  PCard = 7
  Card_5U = 8
  Card_5R = 9
  TCard = 10
  FCard = 11
  ActiveCard = 12
  ComCardUp = 13
  ComCardPro = 14
  ComCardAir = 15


class DayOfWeek(IntEnum):
  """
  Day of week enumeration.
  Sunday == 0 ... Saturday == 6
  """
  # References:
  # PCPROG5 (p. 17)
  # SPORTident 9e291aa \DayOfWeek.cs
  Sunday = 0
  Monday = 1
  Tuesday = 2
  Wednesday = 3
  Thursday = 4
  Friday = 5
  Saturday = 6
  NotSetOrInvalid = 7
  Sun = 0
  Mon = 1
  Tue = 2
  Wed = 3
  Thu = 4
  Fri = 5
  Sat = 6
  Su = 0
  Mo = 1
  Tu = 2
  We = 3
  Th = 4
  Fr = 5
  Sa = 6


class EvaluationStatus(IntEnum):
  # References:
  # SPORTident 9e291aa \EvaluationStatus.cs
  NotSet = 0
  Pending = 1
  Finished = 2
  Lapped = 3
  DidNotStart = -1
  DidNotFinish = -2
  Disqualified = -3
  NotPlaced = -4
  NotCompetitive = -5


class EventForm(IntEnum):
  # References:
  # SPORTident 9e291aa \EventForm.cs
  Single = 0
  Relay = 1


class FractionType(IntEnum):
  # References:
  # SPORTident 9e291aa \FractionType.cs
  None_ = 0
  One50Th = 50
  One256Th = 256


class HalfDay(IntEnum):
  # References:
  # PCPROG5 (pp. 17, 19)
  am = 0
  pm = 1


class MSMode(IntEnum):
  # TODO: Source.
  Master = 77
  Slave = 83


class OperatingMode(IntEnum):
  # References:
  # SPORTident 9e291aa \OperatingMode.cs
  Unknown = 0
  DControl = 1
  Control = 2
  Start = 3
  Finish = 4
  Readout = 5
  ClearKeepStno = 6
  Clear = 7
  Check = 10
  Printout = 11
  StartWithTime = 12
  FinishWithTime = 13
  BcDControl = 17
  BcControl = 18
  BcStart = 19
  BcFinish = 20
  BcLineMasSta = 28
  BcLineMasFin = 29
  BcLineSlave1 = 30
  BcLineSlave2 = 31


class StampSource(IntEnum):
  # References:
  # SPORTident 9e291aa \StampSource.cs
  Readout = 0
  Online = 1
  Backup = 2
  RadioReadout = 3


del IntEnum
