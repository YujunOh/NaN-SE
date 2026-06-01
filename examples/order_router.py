"""순환복잡도 예시. 복잡도가 높으면 완전한 테스트가 어렵다는 강의 메시지를 보이려는 샘플.

route 하나에 결제 수단·지역·회원 등급·재고 분기가 다 들어 있다. 경로 수가
곱으로 늘어 모든 경로를 시험하기 어렵다. nanse analyze로 돌리면 radon이
순환복잡도를 재고 임계 10을 넘으면 finding이 뜬다.
"""


def route(order, member, region, stock):
    if order["method"] == "card":
        if region == "KR":
            if member["grade"] == "vip":
                fee = 0
            elif member["grade"] == "gold":
                fee = 500
            else:
                fee = 1000
        elif region == "US":
            fee = 2000 if member["grade"] == "vip" else 3000
        else:
            fee = 5000
    elif order["method"] == "bank":
        if region == "KR":
            fee = 0 if member["grade"] in ("vip", "gold") else 300
        else:
            fee = 4000
    elif order["method"] == "point":
        if member["points"] < order["amount"]:
            raise ValueError("포인트 부족")
        fee = 0
    else:
        raise ValueError("지원 안 하는 결제 수단")

    if stock.get(order["sku"], 0) < order["qty"]:
        if order.get("backorder"):
            status = "backordered"
        else:
            raise ValueError("재고 부족")
    else:
        status = "ready"

    return {"fee": fee, "status": status}
