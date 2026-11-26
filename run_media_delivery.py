import json
import argparse

from src.infrai_sms import InfraiSms
from src.media_delivery import CreatorDelivery, resend_stuck_delivery


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("message_id")
    parser.add_argument(
        "--send",
        action="store_true",
        help="actually resend the stuck message; omit for a dry run",
    )
    args = parser.parse_args()
    delivery = CreatorDelivery(message_id=args.message_id, creator_id="creator-demo", state="stuck")
    if not args.send:
        print(json.dumps({"message_id": delivery.message_id, "state": delivery.state, "resent": False, "dry_run": True}, sort_keys=True))
        return
    result = resend_stuck_delivery(delivery, InfraiSms())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
