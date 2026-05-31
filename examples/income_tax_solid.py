"""OCP·DIP 위반 예시. 강의 시험 복습에서 다룬 소득세 계산 구조를 옮긴 것.

ComputeTaxUI가 IncomeTax를 직접 만들어 쓰고, IncomeTax.compute가 국가 종류를
if 분기로 다 들고 있다. 프랑스 소득세를 추가하려면 compute 본문을 고쳐야 하고
(개방-폐쇄 위반), UI가 구체 클래스에 직접 묶여 있다(의존 역전 위반).

softgate는 OCP/DIP를 결정론적으로 검출하지 않는다. 확률적 채점을 신뢰하지 않기로
했기 때문이다. 이 파일은 학습 카드 설명층과 보고서에서 개념 예시로 쓰인다.
compute 순환복잡도는 7로 임계 10 미만이라 analyze에서 finding은 안 뜬다.
검출로 잡히지 않는 위반이 있다는 점 자체가 결정론적 검출의 한계 예시다.
"""


class IncomeTax:
    def __init__(self, income):
        self.income = income

    def compute(self, country):
        if country == "KR":
            if self.income <= 12_000_000:
                return self.income * 0.06
            if self.income <= 46_000_000:
                return self.income * 0.15 - 1_080_000
            return self.income * 0.24 - 5_220_000
        if country == "US":
            if self.income <= 11_000:
                return self.income * 0.10
            if self.income <= 44_725:
                return self.income * 0.12
            return self.income * 0.22
        raise ValueError(f"지원 안 하는 국가: {country}")


class ComputeTaxUI:
    def __init__(self, income, country):
        self.tax = IncomeTax(income)
        self.country = country

    def render(self):
        amount = self.tax.compute(self.country)
        return f"{self.country} 소득세: {amount:,.0f}원"
