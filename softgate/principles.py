"""SW공학 원칙 enum. 메트릭과 학습 카드가 공유한다."""

from enum import Enum


class Principle(str, Enum):
    SRP = "Single Responsibility"
    OCP = "Open-Closed"
    LSP = "Liskov Substitution"
    ISP = "Interface Segregation"
    DIP = "Dependency Inversion"
    HIGH_COHESION = "High Cohesion"
    LOW_COUPLING = "Low Coupling"
