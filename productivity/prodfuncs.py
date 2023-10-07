import math
import pandas as pd

def ttm(h, m=0):
  return h * 60 + m

def durationCalc(li, i1=0, i2=1):
  dur = 0
  for l in li:
    dur += l[i2] - l[i1]
  return dur


def finalizer(dic):
  for day in dic:
    for i in range(len(dic[day])):
      tsk = dic[day][i]
      task = tsk[0]
      t1 = tsk[1][0]
      t2 = tsk[1][1]
      t1 = [t1 // 60, t1 % 60, "AM"] if t1 // 60 <= 12 else [(t1 // 60) %
                                                             12, t1 % 60, "PM"]
      t2 = [t2 // 60, t2 % 60, "AM"] if t2 // 60 <= 12 else [(t2 // 60) %
                                                             12, t2 % 60, "PM"]
      dic[day][i] = [task, [t1, t2]]
  return dic


def scheduler(tasks, slots):
  days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
  scheduled = {}
  cdate = pd.to_datetime("today").utcnow().tz_convert('Asia/Kolkata')
  cday = cdate.dayofweek
  first = True
  while tasks:
    day = days[cday]
    scheduled[cdate.strftime("%d-%m-%Y")] = []
    for slot in slots[day]:
      if first:
        if slot[1][0]<(cdate.hour*60+cdate.minute):
          continue
        else:
          first = False
      if slot[0] != 's' and slot[0] != 'ps':
        scheduled[cdate.strftime("%d-%m-%Y")].append(slot)
        continue
      cdur = slot[1][0]
      slotdur = slot[1][1] - slot[1][0]
      while cdur <= slot[1][1]:
        taskdur = []
        i = min([pd.to_datetime(x[2], dayfirst=True) for x in tasks ]) + pd.to_timedelta(1, unit='d')#1
        while not taskdur:
          taskdur = [
            x[1] for x in tasks
            if pd.to_datetime(x[2], dayfirst=True) <= i
          ]
          #i += 1
        ortaskdur = sorted(taskdur)
        index = taskdur.index(min(ortaskdur, key=lambda x: abs(x - slotdur)))

        tsk = tasks[index]
        e = min(taskdur[index], slotdur - cdur + slot[1][0])

        if e == 0:
          break
        scheduled[cdate.strftime("%d-%m-%Y")].append(
          [tsk[0], [cdur, cdur + e]])
        cdur += e
        if e == taskdur[index]:
          tasks.pop(index)
          if not tasks:
            return scheduled
        else:
          tasks[index][1] -= e
    cday = (cday + 1) % 7
    first = False
    cdate += pd.to_timedelta(1, unit='d')
  return scheduled


def slotter(freetime, fixedwtime, n, ratio):
  slots = {}
  for day in freetime:
    slots[day] = []
    a = fixedwtime.get(day, [])
    for ft in a:
      slots[day].append(['ps', ft])

  for day in freetime:
    sdur = durationCalc(fixedwtime.get(day, [[0, 0]]))
    dur = durationCalc(freetime[day]) + sdur

    slfun = math.ceil(dur * (ratio[0]) / (ratio[0] + ratio[1]))
    slstudy = min(math.ceil(dur * (ratio[1]) / (ratio[0] + ratio[1])),
                  dur - slfun)

    slfun += slstudy % 15
    slstudy -= slstudy % 15

    ctime = 0
    turn = 1
    for timeslot in freetime[day]:
      while ctime < timeslot[1]:
        ctime = max(ctime, timeslot[0])
        for key in n.keys():
          skey = key.split(',')
          if key.count(',') == 1 and int(skey[0]) <= ctime <= int(skey[1]):
            nt = n[key] * 15
            break
        else:
          nt = n['default'] * 15
        nt = min(nt, slstudy - sdur)
        if nt <= 15:
          turn = 2
          funtime = timeslot[1] - ctime

        if turn == 1 and ctime + nt <= timeslot[1]:
          slots[day].append(['s', [ctime, ctime + nt]])
          funtime = round(math.ceil(nt * (slfun / slstudy)), -1)
          ctime += nt
          sdur += nt
          turn = 2
        elif turn == 2 and ctime + funtime <= timeslot[1]:
          slots[day].append(['f', [ctime, ctime + funtime]])
          ctime += funtime
          turn = 1
        else:
          slots[day].append(['e', [ctime, timeslot[1]]])
          ctime += timeslot[1] - ctime

  for day, timeslots in slots.items():
      timeslots.sort(key=lambda x:x[1])
  return slots


# vmc = [[ttm(20, 45), ttm(22, 30)]]
# nonvmc = [[ttm(16), ttm(22, 30)]]
# hday = [[ttm(11), ttm(23)]]
# freetime = {
#   "Mo": vmc,
#   "Tu": nonvmc,
#   "We": vmc,
#   "Th": nonvmc,
#   "Fr": vmc,
#   "Sa": hday,
#   "Su": hday
# }

# fixedwtime = {
#   'Mo': [[ttm(5, 30), ttm(6, 30)]],
#   'Tu': [[ttm(5, 30), ttm(6, 30)]],
#   'We': [[ttm(5, 30), ttm(6, 30)]],
#   'Th': [[ttm(5, 30), ttm(6, 30)]],
#   'Fr': [[ttm(5, 30), ttm(6, 30)]]
# }

# #[task, time it gonna take, deadline(date)]
# tasks = sorted(
#   [["Math", ttm(2), '3/12/2022'],
#    ["Computer Science", ttm(4, 30), '5/12/2022'],
#    ["English", ttm(1), '2/12/2022'], ["Chemistry",
#                                        ttm(5), '3/12/2022'],
#    ["Physics", ttm(4, 45), '4/12/2022']],
#   key=lambda x: pd.to_datetime(x[2]))


# ratio = [2, 3]  #fun:study

# n = {
#   'default': 4,
#   f"{ttm(11)},{ttm(19)}": 6
# }  #amount of study time per session (in 15 mins)

# slots = slotter(freetime, fixedwtime, n, ratio)
# #date -> "12/11/2022"


# owo = finalizer(scheduler(tasks, slots))

def finalmsg(scheduled, day=pd.to_datetime('today').strftime('%d-%m-%Y')):
    if day not in scheduled:
      return None
    days = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]
    msg = f"\n**{days[pd.to_datetime(day, dayfirst=True).dayofweek]}**"
    for scheds in scheduled[day]:
        start = scheds[1][0]
        end = scheds[1][1]
        task = scheds[0] if scheds[0] != 'f' else 'Leisure'
        msg += f"\n{start[0]}:{start[1]} {start[2]} - {end[0]}:{end[1]} {end[2]} : {task}"
    return msg
  