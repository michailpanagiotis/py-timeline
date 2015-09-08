# py-timeline
A timeline to log and track events


## Usage

```
>>> from timeline import Timeline, Event
>>> timeline = Timeline()
>>> timeline.append(Event(status='created'))
>>> timeline
Timeline(Event({'status': 'created'} 1441716885))
>>> timeline.append(Event(status='updated', changes=['1', '2', '3']))
>>> timeline
Timeline(Event({'status': 'created'} 1441716885),Event({'status': 'updated', 'changes': ['1', '2', '3']} 1441716948))
>>> timeline.append(Event(status='soft deleted'))
>>> timeline[-1]
Event({'status': 'soft deleted'} 1441716980)
>>> timeline[1]['status']
'updated'
>>> timeline.trim(2)
>>> timeline
Timeline(Event({'status': 'updated', 'changes': ['1', '2', '3']} 1441716948),Event({'status': 'soft deleted'} 1441716980))
```
