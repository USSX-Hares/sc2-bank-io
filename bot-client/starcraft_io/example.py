import json
import sys

from starcraft_io.bank_api import BankImpl
from starcraft_io.events_api import *

if (__name__ == '__main__'):
    pass

b = BankImpl.open \
(
    bank_name = 'bankio',
    test_run = True,
)

for line in b.dump():
    print(line)
print()

json.dump(b.as_dict(), sys.stdout, indent=4)
print()
print()

eb = EventsBank(b)
print(eb)

responses = list(eb.event_ids(MessageType.Response, pop=True))
print(responses)
for resp in responses:
    print(eb.pop_event(resp, MessageType.Response))
eb.add_event(PingEvent.new_request())
eb.save()
print()
