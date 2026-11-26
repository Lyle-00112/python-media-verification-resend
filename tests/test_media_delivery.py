from src.media_delivery import CreatorDelivery, resend_stuck_delivery


class FakeSms:
    def __init__(self):
        self.calls = []

    def resend(self, message_id):
        self.calls.append(("resend", message_id))
        return {"ok": True}

    def events(self, message_id):
        self.calls.append(("events", message_id))
        return {"ok": True, "data": {"status": "delivered"}}


def test_stuck_delivery_is_resent_and_state_is_returned():
    client = FakeSms()
    result = resend_stuck_delivery(
        CreatorDelivery("msg-42", "creator-7", "stuck"), client
    )

    assert result == {"message_id": "msg-42", "state": "delivered", "resent": True}
    assert client.calls == [("resend", "msg-42"), ("events", "msg-42")]


def test_delivered_delivery_is_not_sent_again():
    client = FakeSms()
    result = resend_stuck_delivery(
        CreatorDelivery("msg-42", "creator-7", "delivered"), client
    )

    assert result["resent"] is False
    assert client.calls == []

