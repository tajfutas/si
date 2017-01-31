from enum import Enum


class SimSrrFrequencyChannels(Enum):
  # References:
  # SPORTident.Communication 9e291aa \SimSrrFrequencyChannels.cs
  NotSet = -1
  Red = 0
  Blue = 1
  Yellow = 2
  Green = 3


del Enum
