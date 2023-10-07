import discord, json
from discord.ext import commands
from discord import app_commands
from requests import get
from discord.ui import Button, View, Select, Modal, TextInput
import pandas as pd
from productivity.prodfuncs import slotter, scheduler, finalizer, finalmsg, ttm
import traceback

class Todo(View):
    def __init__(self, ctx, client):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.client = client

    @discord.ui.button(label="Add Task", style=discord.ButtonStyle.blurple)
    async def add_button_callback(self, interaction, button):
        await self.disable_all()

        await interaction.response.send_message(
            "Type the task name, duration (in mins) and deadline (DD/MM/YYYY) seprated by @ to add it to your list!\neg. read a book @ 60 @ 1/12/2022",
            delete_after=8,
            ephemeral=True)

        def check(msg):
            return msg.author == self.ctx.author and msg.channel == self.ctx.channel

        msg = await self.client.wait_for("message", check=check)
        await msg.delete(delay=3)

        if msg.content.count('@')>=2:
            [task,duration,deadline] = msg.content.split('@')[:3]
            try:
                if int(duration)<30 or int(duration)>720:
                    await self.ctx.send('Invalid duration, needs to be between 30-720.')
                    int('hola')
                deadline = pd.to_datetime(deadline.replace(' ',''), dayfirst=True)
                add(task.strip(), self.ctx.author.id, int(duration), deadline.strftime('%d-%m-%Y'))
            except:
                pass
        else:
            add(msg.content, self.ctx.author.id)

        em = get_embed(self.ctx.author)

        view = Todo(self.ctx, self.client)
        view.message = await self.message.edit(embed=em, view=view)
	
    @discord.ui.button(label="Edit Task", style=discord.ButtonStyle.blurple)
    async def edit_button_callback(self, interaction, button):
        await self.disable_all()

        await interaction.response.send_message(
            "Type the index, task name, duration (in mins) and deadline (DD/MM/YYYY) seprated by @ to edit it!\neg. 2 @ read a book @ 60 @ 1/12/2022",
            delete_after=8,
            ephemeral=True)

        def check(msg):
            return msg.author == self.ctx.author and msg.channel == self.ctx.channel

        msg = await self.client.wait_for("message", check=check)
        await msg.delete(delay=3)

        try:
            if msg.content.count('@') == 1:
                [index, task] = msg.content.split('@')[:2]
                i = int(index)
                edit(i, task.strip(), self.ctx.author.id)
            elif msg.content.count('@') >= 3:
                [index, task, duration, deadline] = msg.content.split('@')[:4]
                i = int(index)
                if int(duration) < 30 or int(duration) > 720:
                    await self.ctx.send('Invalid duration, needs to be between 30-720.')
                    int('hola')
                deadline = pd.to_datetime(
                    deadline.replace(' ', ''), dayfirst=True)
                edit(i, task.strip(), self.ctx.author.id, int(duration),
                     deadline.strftime('%d-%m-%Y'))
        except:
            pass

        em = get_embed(self.ctx.author)

        view = Todo(self.ctx, self.client)
        view.message = await self.message.edit(embed=em, view=view)
        
    @discord.ui.button(label="Remove Task", style=discord.ButtonStyle.blurple)
    async def remove_button_callback(self, interaction, button):
        await self.disable_all()
        await interaction.response.send_message(
            "Type the task index number to remove it from your list!",
            delete_after=8,
            ephemeral=True)

        def check(msg):
            return msg.author == self.ctx.author and msg.channel == self.ctx.channel

        num = await self.client.wait_for("message", check=check)
        await num.delete(delay=3)
        remove(num.content, self.ctx.author.id)
        em = get_embed(self.ctx.author)

        view = Todo(self.ctx, self.client)
        view.message = await self.message.edit(embed=em, view=view)

    @discord.ui.button(label="Clear", style=discord.ButtonStyle.blurple)
    async def clear_button_callback(self, interaction, button):

        self.clear_items()
        button = Button(label="Confirm", style=discord.ButtonStyle.red)
        button.callback = self.confirm_clear
        self.add_item(button)

        button = Button(label="Back", style=discord.ButtonStyle.grey)
        button.callback = self.back
        self.add_item(button)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def done_button_callback(self, interaction, button):
        self.clear_items()
        await interaction.response.edit_message(view=self)

    async def confirm_clear(self, interaction):
        await interaction.response.defer()
        removeall(self.ctx.author.id)
        em = get_embed(self.ctx.author)
        view = Todo(self.ctx, self.client)
        view.message = await self.message.edit(view=view, embed=em)

    async def back(self, interaction):
        await interaction.response.defer()
        view = Todo(self.ctx, self.client)
        view.message = await self.message.edit(view=view)

    async def disable_all(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot use that!",
                                                    ephemeral=True)
            return False
        else:
            return True


class Profile(View):
    def __init__(self, ctx, client):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.client = client

    @discord.ui.button(label="General", style=discord.ButtonStyle.green)
    async def general_button_callback(self, interaction, button):
        em = get_prof_embed(self.ctx.author, "general")

        view = Profile(self.ctx, self.client)

        button = Button(label="Ratio", style=discord.ButtonStyle.blurple, row=1)
        button.callback = self.ratio
        view.add_item(button)

        button = Button(label="Minimum Work Time", style=discord.ButtonStyle.blurple, row=1)
        button.callback = self.minwt
        view.add_item(button)
        await interaction.response.edit_message(view=view, embed=em)

    @discord.ui.button(label="Free Time", style=discord.ButtonStyle.green)
    async def ft_button_callback(self, interaction, button):
        em = get_prof_embed(self.ctx.author, "ft")

        view = Profile(self.ctx, self.client)
        for r,i in enumerate(["Mo","Tu","We","Th","Fr","Sa","Su"]):
            button = Button(label=i,custom_id='ft'+i, style=discord.ButtonStyle.blurple, row=1 if r<5 else 2)
            button.callback = self.ffwtt
            view.add_item(button)

        await interaction.response.edit_message(view=view, embed=em)
    
    @discord.ui.button(label="Fixed Work Time", style=discord.ButtonStyle.green)
    async def fwt_button_callback(self, interaction, button):
        em = get_prof_embed(self.ctx.author, "fwt")

        view = Profile(self.ctx, self.client)
        for r,i in enumerate(["Mo","Tu","We","Th","Fr","Sa","Su"]):
            button = Button(label=i, custom_id='fw'+i, style=discord.ButtonStyle.blurple, row=1 if r<5 else 2)
            button.callback = self.ffwtt
            view.add_item(button)

        await interaction.response.edit_message(view=view, embed=em)
    
    
    async def empty_callback(self, interaction):
        await interaction.response.defer()

    async def ffwtt(self, interaction):
        self.clear_items()
        butid = interaction.data["custom_id"]
        day = butid[2:]
        if butid[:2]=="ft":
            loc = "freetime"
            page = "ft"
        else:
            loc = "fixedwtime"
            page= "fwt"
        sh = Select(placeholder="Start Hour", options=[discord.SelectOption(label=i) for i in range(24)])
        sm = Select(placeholder="Start Minute", options=[discord.SelectOption(label=i) for i in range(0,46,15)])
        eh = Select(placeholder="End Hour", options=[discord.SelectOption(label=i) for i in range(24)])
        em = Select(placeholder="End Minute", options=[discord.SelectOption(label=i) for i in range(0,46,15)])
        submit = Button(label='Submit', style=discord.ButtonStyle.green)
        reset = Button(label="Reset", style=discord.ButtonStyle.red)
        sh.callback = sm.callback = eh.callback = em.callback = self.empty_callback
        self.add_item(sh)
        self.add_item(sm)
        self.add_item(eh)
        self.add_item(em)
        self.add_item(submit)
        self.add_item(reset)

        async def ftdone(interaction):
            if sh.values==[] or sm.values==[] or eh.values==[] or em.values==[]:
                await self.ctx.send(f'Invalid Time!', delete_after=5)
            else:
                time = [ttm(int(sh.values[0]),int(sm.values[0])),ttm(int(eh.values[0]),int(em.values[0]))]
                x = addtime(self.ctx.author.id, day, time, loc)
                if x:
                    if loc=="freetime":
                        await self.ctx.send(f'Time added to free time!', delete_after=5)
                        
                    else:
                        await self.ctx.send(f'Time added to fixed work time!', delete_after=5)
                        
                else:
                    await self.ctx.send(f'Invalid Time!', delete_after=5)
            view = Profile(self.ctx, self.client)
            emb = get_prof_embed(self.ctx.author,page)
            await interaction.response.edit_message(view=view, embed=emb)

        async def ftreset(interaction):
            with open('productivity/profile.json', 'r+') as f:
                json_data = json.load(f)
                data = json_data.get(f'{self.ctx.author.id}')
                data[loc][day] = []
                f.seek(0)
                f.write(json.dumps(json_data))
                f.truncate()
            view = Profile(self.ctx, self.client)
            emb = get_prof_embed(self.ctx.author,page)
            await interaction.response.edit_message(view=view, embed=emb)

        submit.callback = ftdone
        reset.callback = ftreset
        await interaction.response.edit_message(view=self)


    async def ratio(self, interaction):
        self.clear_items()
        leisure = Select(placeholder="Leisure", options=[discord.SelectOption(label=i) for i in range(1,6)])
        work = Select(placeholder="Work", options=[discord.SelectOption(label=i) for i in range(1,6)])
        submit = Button(label='Submit', style=discord.ButtonStyle.green)
        self.add_item(leisure)
        self.add_item(work)
        self.add_item(submit)

        async def ratiodone(interaction):
            if leisure.values != [] and work.values != []:
                set_ratio(self.ctx.author.id, [int(leisure.values[0]), int(work.values[0])])
                await self.ctx.send(f'Ratio set to {leisure.values[0]}:{work.values[0]}!', delete_after=5)
                
            view = Profile(self.ctx, self.client)
            em = get_prof_embed(self.ctx.author)
            await interaction.response.edit_message(view=view,embed=em)
        
        leisure.callback = work.callback = self.empty_callback
        submit.callback= ratiodone

        await interaction.response.edit_message(view=self)
    
    
    async def minwt(self, interaction):
        self.clear_items()
        n = Select(placeholder="Minimum Work Time", options=[discord.SelectOption(label=f"{i} mins", value=i//15) for i in range(30,121,15)])
        self.add_item(n)

        reset = Button(label='Reset', style=discord.ButtonStyle.red)
        self.add_item(reset)
        sh = Select(placeholder="Start Hour", options=[discord.SelectOption(label=i) for i in range(24)])
        sm = Select(placeholder="Start Minute", options=[discord.SelectOption(label=i) for i in range(0,46,15)])
        eh = Select(placeholder="End Hour", options=[discord.SelectOption(label=i) for i in range(24)])
        em = Select(placeholder="End Minute", options=[discord.SelectOption(label=i) for i in range(0,46,15)])
        submit = Button(label='Submit', style=discord.ButtonStyle.green)
        
        async def minwttime(interaction):
            if sh.values==[] or sm.values==[] or eh.values==[] or em.values==[]:
                set_minwt(self.ctx.author.id, n.values[0])
                await self.ctx.send(f'Minimum work time set to {int(n.values[0])*15} mins!', delete_after=5)
            else:
                time = [ttm(int(sh.values[0]),int(sm.values[0])),ttm(int(eh.values[0]),int(em.values[0]))]
                x = set_minwt(self.ctx.author.id, n.values[0], time)
                if x:
                    await self.ctx.send(f'Minimum work time set to {sh.values[0]}:{sm.values[0]}-{eh.values[0]}:{em.values[0]}: {int(n.values[0])*15} mins!', delete_after=5)
                else:
                    await self.ctx.send(f'Invalid Time!', delete_after=5)
            view = Profile(self.ctx, self.client)
            emb = get_prof_embed(self.ctx.author)
            await interaction.response.edit_message(view=view, embed=emb)

        async def minwtdone(interaction):
            self.clear_items()
            sh.callback = sm.callback = eh.callback = em.callback = self.empty_callback
            self.remove_item(n)
            self.add_item(sh)
            self.add_item(sm)
            self.add_item(eh)
            self.add_item(em)
            self.add_item(submit)
            submit.callback = minwttime
            await interaction.response.edit_message(view=self)
        
        async def minwtreset(interaction):
            with open('productivity/profile.json', 'r+') as f:
                json_data = json.load(f)
                data = json_data.get(f'{self.ctx.author.id}')
                default = data['n']['default']
                data['n'] = {"default":default}
                f.seek(0)
                f.write(json.dumps(json_data))
                f.truncate()

            view = Profile(self.ctx, self.client)
            emb = get_prof_embed(self.ctx.author)
            await interaction.response.edit_message(view=view, embed=emb)

        n.callback = minwtdone
        reset.callback = minwtreset 
        await interaction.response.edit_message(view=self)
    

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def done_button_callback(self, interaction, button):
        self.clear_items()
        await interaction.response.edit_message(view=self)

    async def disable_all(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot use that!",
                                                    ephemeral=True)
            return False
        else:
            return True

class Productivity(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # @commands.command(hidden=True)
    # async def sync(self,ctx):
    #     if ctx.author.id == 591825462393569294:
    #         print(ctx.author.id, type(ctx.author.id))
    #         fmt = await self.client.tree.sync()
    #         await ctx.send(f"Synced {len(fmt)} commands.")

    @commands.command(description="Sends an inspirational quote.")
    async def quote(self, ctx):
        quote = None
        c = 0
        while not quote:
            if c>5:
                await ctx.send("Failed to fetch quote. Try again later.")
                return
            try:
                response = get(
                    'http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en'
                )
                quote = json.loads(response.text)
            except:
                pass
            c += 1

        em = discord.Embed()
        if not quote["quoteAuthor"]:
            quote["quoteAuthor"] = 'Unknown'
        em.add_field(name=quote["quoteAuthor"] + '-',
                     value=quote["quoteText"],
                     inline=False)
        await ctx.send(embed=em)

    @commands.command(description="Shows your todo list.")
    async def todo(self, ctx):
        checkadduser(ctx.author.id)
        em = get_embed(ctx.author)
        view = Todo(ctx, self.client)
        view.message = await ctx.send(embed=em, view=view)

    @commands.command(description="For setting your profile.")
    async def profile(self,ctx):
        checkuserprof(ctx.author.id)
        em = get_prof_embed(ctx.author)
        view = Profile(ctx, self.client)
        view.message = await ctx.send(embed=em, view=view)

    @commands.command(description="Auto Scheduler!")
    async def autosched(self,ctx):
        try:
            checkuserprof(ctx.author.id)
        
            dates = []
            c = 0
            sched = get_schedule(ctx.author.id)
            msg = None
            while msg or c<=1:
                date = (pd.to_datetime("today") + pd.to_timedelta(c, unit='d')).strftime('%d-%m-%Y')
                msg = finalmsg(sched, date)
                if msg:
                    dates.append(date)
                c+=1

            if dates == []:
                await ctx.send('Add tasks to use auto scheduler!')
                return

            dates = dates[:14]
            async def datemenu_callback(interaction):
                msg = finalmsg(sched, datemenu.values[0])        
                em = discord.Embed()
                em.set_thumbnail(url=ctx.author.avatar)
                em.add_field(name=f"{ctx.author.name}'s Schedule for {datemenu.values[0]}", value=msg)
            
                await interaction.response.edit_message(embed=em)

            datemenu = Select(placeholder="Select Date", options=[discord.SelectOption(label=i) for i in dates])
            datemenu.callback = datemenu_callback

            view = View()
            view.add_item(datemenu)

            msg = finalmsg(sched, dates[0])        
            em = discord.Embed()
            em.set_thumbnail(url=ctx.author.avatar)
            em.add_field(name=f"{ctx.author.name}'s Schedule for {date}", value=msg)
            await ctx.send(embed=em, view=view)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            #raise e
            #print(e)

        

async def setup(client):
    await client.add_cog(Productivity(client))


def checkuserprof(id):
    with open('productivity/profile.json', 'r+') as f:
        json_data = json.load(f)
        try:
            data = json_data[f'{id}']
        except KeyError:
            json_data[f'{id}'] = { "n": {"default":4}, "freetime": {'Mo': [],'Tu': [],'We': [],'Th': [],'Fr': [],'Sa': [],'Su': []}, "fixedwtime": {'Mo': [],'Tu': [],'We': [],'Th': [],'Fr': [],'Sa': [],'Su': []}, "ratio":[1,1]}
            f.seek(0)
            f.write(json.dumps(json_data))
            f.truncate()


def checkadduser(id):
    with open('productivity/todo.json', 'r+') as f:
        json_data = json.load(f)
        try:
            data = json_data[f'{id}']
        except KeyError:
            json_data[f'{id}'] = {}
            f.seek(0)
            f.write(json.dumps(json_data))
            f.truncate()


def add(task, id, duration=None,deadline=None):
    with open('productivity/todo.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data[f'{id}']
        if len(data) >= 50:
            return False
        if deadline and duration:
            data[f'{len(data)+1}'] = [task, duration, deadline]
        else:
            data[f'{len(data)+1}'] = task
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate()

def edit(index, task, id, duration=None, deadline=None):
    with open('productivity/todo.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data[f'{id}']
        length = len(data)
        if length < index or index <= 0:
            return False

        if deadline and duration:
            data[f'{index}'] = [task, duration, deadline]
        else:
            data[f'{index}'] = task
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate()
        
def remove(num, id):
    try:
        num = int(num)
    except:
        return
    with open('productivity/todo.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data[f'{id}']
        length = (len(data))
        if length < num or num <= 0:
            return False
        for i in range(num, length):
            data[f'{i}'] = data[f'{i+1}']
        data.pop(str(length))
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate()
        return True


def removeall(id):
    with open('productivity/todo.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data[f'{id}']
        length = (len(data))
        if length == 0:
            return False
        json_data[f'{id}'] = {}
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate()
        return True


def get_embed(author):
    with open('productivity/todo.json', 'r') as f:
        json_data = json.load(f)
        data = json_data[f'{author.id}']
    em = discord.Embed()
    em.set_thumbnail(url=author.avatar)
    if data:
        #return await ctx.send("Please add a task first.", delete_after=5)
        tasks = '```\n‎'
        for key in data:
            if type(data[key])==type(''):
                task = data[key]
                duration = ''
                deadline = ''
            else:
                task = data[key][0]
                duration = f"[Dur: {data[key][1]//60}h {data[key][1]%60}m"
                deadline = f"Due: {data[key][2]}]"
            nkey = key
            if len(key) == 1:
                nkey = "0" + key
            tasks += f"\n{nkey}.  {task} {duration} {deadline}"
        tasks += '```'
        em.add_field(name=author.name + "'s Todo List", value=tasks)
    else:
        em.add_field(name=author.name + "'s Todo List",
                     value="\n```\nNo Tasks...```")
    return em

def get_prof_embed(author, page="general"):
    with open('productivity/profile.json', 'r') as f:
        json_data = json.load(f)
        data = json_data[f'{author.id}']
    em = discord.Embed()
    em.set_thumbnail(url=author.avatar)

    msg = '```\n‎'
    if page=="general":
        msg += f"\nRatio (Leisure:Work): {data['ratio'][0]}:{data['ratio'][1]}"
        msg += f"\nMinimum Work Time (per session): "
        for key in data["n"]: 
            if key.count(',') == 1:
                m = key.split(',')
                m = [int(i) for i in m]
                msg += f"\n {m[0]//60}:{m[0]%60} - {m[1]//60}:{m[1]%60} : {data['n'][key]*15} mins"
            else:
                msg += str(data["n"]['default']*15) + ' mins'
    elif page=="ft":
        msg += "\nFree Time:"
        for key in data["freetime"]:
            msg += f"\n{key}: "
            for timeslot in data["freetime"][key]:
                msg += f"{timeslot[0]//60}:{timeslot[0]%60} - {timeslot[1]//60}:{timeslot[1]%60}, "

    elif page=="fwt":
        msg += "\nFixed Work Time:"
        for key in data["fixedwtime"]:
            msg += f"\n{key}: "
            for timeslot in data["fixedwtime"][key]:
                msg += f"{timeslot[0]//60}:{timeslot[0]%60} - {timeslot[1]//60}:{timeslot[1]%60}, "
    
    msg += '```'
    em.add_field(name=author.name + "'s Scheduler Profile", value=msg)
    
    return em

def set_ratio(id, ratio):
    with open('productivity/profile.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data.get(f'{id}')
        data["ratio"] = ratio
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate()
    return True

def checkTimeClash(time, tl):
    start = time[0]
    end = time[1]
    if start>=end:
        return True
    for t in tl:
        s1 = t[0]
        e1 = t[1]
        if s1<=start<e1 or s1<end<=e1:
            return True
    return False

def set_minwt(id, n, time=None):
    with open('productivity/profile.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data.get(f'{id}')
        if not time:
            data["n"]["default"] = int(n)
        else:
            tl=[]
            for key in data["n"].keys():
                if key.count(',') == 1:
                    tl.append([int(i) for i in key.split(',')])
            if checkTimeClash(time,tl):
                return False
            t = f"{time[0]},{time[1]}"
            data["n"][t] = int(n)
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate()
    return True


def addtime(id, day, time, loc):
    with open('productivity/profile.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data.get(f'{id}')
        if checkTimeClash(time,data["freetime"][day]) or checkTimeClash(time, data["fixedwtime"][day]):
            return False
        data[loc][day].append(time)
        data[loc][day].sort()
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate()
    return True

def get_schedule(id):
    with open('productivity/profile.json', 'r+') as f:
        json_data = json.load(f)
        data = json_data.get(f'{id}')
        freetime = data['freetime']
        fixedwtime = data['fixedwtime']
        n = data['n']
        ratio = data['ratio']
    with open('productivity/todo.json', 'r') as f:
        json_data = json.load(f)
        data = json_data[f'{id}']
        tasks = sorted([task for key, task in data.items() if type(task)==type([])], key=lambda x: pd.to_datetime(x[2], dayfirst=True))
    slots = slotter(freetime, fixedwtime, n, ratio)
    return finalizer(scheduler(tasks, slots))