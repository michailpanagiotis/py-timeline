# pytimeline
A timeline to log and track events


## Usage
Create events
```
>>> from timeline import Timeline, Event
>>> timeline = Timeline()
>>> timeline.append(Event(status='created'))
>>> timeline
Timeline(Event({'status': 'created'} 1441718935))
>>> timeline.append(Event(status='updated', changes=['1', '2', '3']))
>>> timeline
Timeline(Event({'status': 'created'} 1441718935),Event({'status': 'updated', 'changes': ['1', '2', '3']} 1441718943))
>>> timeline.append(Event(status='soft deleted'))
>>> timeline
Timeline(Event({'status': 'created'} 1441718935),Event({'status': 'updated', 'changes': ['1', '2', '3']} 1441718943),Event({'status': 'soft deleted'} 1441718950))
```
Map
```
>>> stat_codes = {'created': 0, 'updated': 1, 'soft deleted': 2}
>>> timeline2 = timeline.map(lambda x: {'status': stat_codes[x['status']]})
>>> timeline2
Timeline(Event({'status': 0} 1441718935),Event({'status': 1} 1441718943),Event({'status': 2} 1441718950))
```
Filter
```
>>> timeline.filter(lambda x: x['status'] != 'created')
Timeline(Event({'status': 'updated', 'changes': ['1', '2', '3']} 1441718943),Event({'status': 'soft deleted'} 1441718950))
```
Deltas
```
>>> timeline2.deltas(lambda x,y: {'diff': y['status'] - x['status'], 'flag_deleted': y['status'] == 2})
Timeline(Event({'diff': 1, 'flag_deleted': False} 1441718943),Event({'diff': 1, 'flag_deleted': True} 1441718950))
```
Misc
```
>>> timeline.timeframe()
Timeframe(1441718935, 1441718950)
>>> 
>>> timeline.trim(2)
>>> timeline
Timeline(Event({'status': 'updated', 'changes': ['1', '2', '3']} 1441718943),Event({'status': 'soft deleted'} 1441718950))
```
