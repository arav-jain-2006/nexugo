import discord
import random
import json
from discord.ext import commands
from discord import Member, app_commands
from PIL import Image, ImageDraw, ImageFont
import os
from discord.ui import View, Button
# from copy import deepcopy

SIZE = 9  # max 9


class InviteUser(View):
    def __init__(self, member):
        super().__init__(timeout=60)
        self.member = member
        self.value = False

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button_callback(self, interaction, button):
        # await interaction.response.send_message("Hello!")
        for child in self.children:
            child.disabled = True
        self.value = True
        await interaction.response.send_message("Battleship challenge accepted!")
        await interaction.message.edit(view=self)
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button_callback(self, interaction, button):
        for child in self.children:
            child.disabled = True
        await interaction.response.send_message("Battleship challenge declined!")
        await interaction.message.edit(view=self)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="The request has timed out...", view=self)
        return

    async def interaction_check(self, interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("You cannot use that!", ephemeral=True)
            return False
        else:
            return True


class Place(View):

    def __init__(self, battleship_obj, member):
        super().__init__(timeout=None)
        self.battleship_obj = battleship_obj
        self.member = member

        self.coords = self.battleship_obj.coords[self.member.id]
        self.placed = self.battleship_obj.placed[self.member.id]
        self.board = self.battleship_obj.boards[self.member.id]

        self.item = self.alph = self.num = self.ori = None

    @discord.ui.select(placeholder='Item Number', options=[discord.SelectOption(label=f'{i} (Length-{i if i>2 else i+1})', value=str(i)) for i in range(1, 6)])
    async def item_callback(self, interaction, select):
        self.item = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(placeholder='Horizontal Position', options=[discord.SelectOption(label=i) for i in ["A", "B", "C", "D", "E", "F", "G", "H", "I"][:SIZE]])
    async def alph_callback(self, interaction, select):
        self.alph = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(placeholder='Vertical Position', options=[discord.SelectOption(label=i, value=str(n+1)) for n, i in enumerate(["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"][:SIZE])])
    async def num_callback(self, interaction, select):
        self.num = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(placeholder='Orientation', options=[discord.SelectOption(label='Horizontal'), discord.SelectOption(label="Vertical")])
    async def ori_callback(self, interaction, select):
        self.ori = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label='Deploy', style=discord.ButtonStyle.blurple)
    async def place(self, interaction, button):
        if not (self.item and self.num and self.alph and self.ori):
            await interaction.response.send_message("You haven't selected all the required fields.")
            return

        ori = self.ori[0].lower()
        item = int(self.item)
        length = [2, 3, 3, 4, 5]
        pos = code_to_coords(self.alph+self.num)
        item_length = length[item - 1]
        if ori == 'h':
            x = 1
            y = 0
        elif ori == 'v':
            x = 0
            y = 1
        if not (item in self.placed):
            if space_available(self.board, pos, item_length, ori):
                self.placed.append(item)
                self.coords[item] = [pos, ori]

                for i in range(item_length):
                    self.board[pos[1] + (y*i)][pos[0] + (x * i)] = item
            else:
                await interaction.response.send_message('Not enough space available.', ephemeral=True)
                return

        elif space_available(remove_item(self.board, item), pos, item_length,
                             ori):
            self.board = remove_item(self.board, item)
            for i in range(item_length):
                self.board[pos[1] + (y * i)][pos[0] + (x * i)] = item
            self.coords[item] = [pos, ori]
        else:
            await interaction.response.send_message('Not enough space available.', ephemeral=True)
            return

        # file = imager(self.coords, self.member.id)
        # with open(file, "rb") as fh:
        #     image = discord.File(fh, filename=file)

        # my_filename = 'battleship/images/spaceships2.png'
        # with open(my_filename, "rb") as fh:
        #     b = discord.File(fh, filename=my_filename)
        msg = imager(self.coords)
        emb = discord.Embed(title='Setup')
        emb.add_field(name=' ', inline=False, value=msg)

        self.item = self.alph = self.num = self.ori = None
        # attachments=[image, b])
        await interaction.response.edit_message(embed=emb)

        # await interaction.response.defer()

    @discord.ui.button(label='Random', style=discord.ButtonStyle.blurple)
    async def rndmize(self, interaction, button):
        self.coords, self.board = randomize()
        self.placed = [1, 2, 3, 4, 5]
        msg = imager(self.coords)
        emb = discord.Embed(title='Setup')
        emb.add_field(name=' ', inline=False, value=msg)
        # file = imager(self.coords, self.member.id)
        # with open(file, "rb") as fh:
        #     image = discord.File(fh, filename=file)

        # my_filename = 'battleship/images/spaceships2.png'
        # with open(my_filename, "rb") as fh:
        #     b = discord.File(fh, filename=my_filename)

        self.item = self.alph = self.num = self.ori = None
        await interaction.response.edit_message(embed=emb)

    @discord.ui.button(label='Reset', style=discord.ButtonStyle.red)
    async def reset(self, interaction, button):
        self.coords = {}
        self.board = [[0 for i in range(8)] for j in range(8)]
        self.placed = []

        msg = imager({})
        emb = discord.Embed(title='Setup')
        emb.add_field(name=' ', inline=False, value=msg)
        # file = imager(self.coords, self.member.id)
        # with open(file, "rb") as fh:
        #     image = discord.File(fh, filename=file)

        # my_filename = 'battleship/images/spaceships2.png'
        # with open(my_filename, "rb") as fh:
        #     b = discord.File(fh, filename=my_filename)

        self.item = self.alph = self.num = self.ori = None
        await interaction.response.edit_message(embed=emb)

    @discord.ui.button(label='Ready', style=discord.ButtonStyle.green)
    async def ready(self, interaction, button):
        if len(self.placed) < 5:
            await interaction.response.send_message('Deploy all the spaceships first!')
            return

        with open('battleship/user_data/setups.json', 'r+') as f:
            json_data = json.load(f)
            json_data[str(self.member.id)] = self.coords
            f.seek(0)
            f.write(json.dumps(json_data))
            f.truncate()

        await interaction.response.send_message('Great, go to the server channel to play!')
        self.clear_items()
        # file = imager(self.coords, self.member.id)
        # with open(file, "rb") as fh:
        #     image = discord.File(fh, filename=file)
        await self.message.edit(view=self)

        await self.battleship_obj.begin(self.member.id, self.board, self.coords)


class Value:
    def __init__(self, v=None):
        self.v = v


class Move(View):

    def __init__(self, player, opponent, battleship_obj):
        super().__init__(timeout=None)

        self.player = player
        self.opponent = opponent

        self.boards = {
            player: battleship_obj.boards[player], opponent: battleship_obj.boards[opponent]}
        self.channel = battleship_obj.battle_data[player].v[0]
        self.coords = {
            player: battleship_obj.coords[player], opponent: battleship_obj.coords[opponent]}

        self.bo = battleship_obj

        self.sboards = {self.player: imager({}), self.opponent: imager({})}

        alph = ["A", "B", "C", "D", "E", "F", "G", "H", "I"][:SIZE]
        nums = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣",
                "6️⃣", "7️⃣", "8️⃣", "9️⃣"][:SIZE]

        for n, i in enumerate(alph):
            b = Button(label=i, custom_id=i,
                       style=discord.ButtonStyle.blurple, row=(0 if n < SIZE/2 else 1))
            b.callback = self.alph_callback
            self.add_item(b)

        for n, i in enumerate(nums):
            b = Button(label=i, custom_id=str(n+1),
                       style=discord.ButtonStyle.blurple, row=(2 if n < SIZE/2 else 3))
            b.callback = self.num_callback
            self.add_item(b)

        self.inf = Button(label='Log', emoji='📜',
                          disabled=True, row=4)
        self.inf.callback = self.empty_callback
        self.add_item(self.inf)

        self.num = None
        self.alph = None

    async def empty_callback(self, interaction):
        await interaction.response.defer()

    async def num_callback(self, interaction):
        l = [str(i) for i in range(1, SIZE+1)]
        self.num = interaction.data['custom_id']
        for child in self.children:
            if child.custom_id == interaction.data['custom_id']:
                child.disabled = True
            elif child.custom_id in l:
                child.disabled = False
        await interaction.response.edit_message(view=self)

    async def alph_callback(self, interaction):
        l = ["A", "B", "C", "D", "E", "F", "G", "H", 'I'][:SIZE]
        self.alph = interaction.data['custom_id']
        for child in self.children:
            if child.custom_id == interaction.data['custom_id']:
                child.disabled = True
            elif child.custom_id in l:
                child.disabled = False
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Fire!', style=discord.ButtonStyle.red, row=4)
    async def fire(self, interaction, button):
        await interaction.response.defer()
        if not (self.alph and self.num):
            # await interaction.response.send_message('')
            return

        self.p = await self.bo.client.fetch_user(self.player)
        self.o = await self.bo.client.fetch_user(self.opponent)

        pos = code_to_coords(self.alph + str(self.num))
        item = self.boards[self.opponent][pos[1]][pos[0]]
        if item != 'X' and item != 'S':
            win = False
            # not already moved here
            # print(self.alph, self.num)
            self.boards[self.opponent][pos[1]][pos[0]] = 'X'
            # print(self.sboards[self.opponent])
            if item != 0:
                # HIT
                if not any(item in row for row in self.boards[self.opponent]):
                    # SINK
                    length = [2, 3, 3, 4, 5]
                    item_length = length[item - 1]
                    coord = self.coords[self.opponent][item][0]
                    orientation = self.coords[self.opponent][item][1]

                    self.sboards[self.opponent] = sink(
                        self.sboards[self.opponent], coord, item, orientation)

                    # await self.channel.send("Ship sunk!", delete_after=5)
                    self.inf.label = 'Destroyed!'
                    self.inf.emoji = '💀'
                    self.boards[self.opponent][pos[1]][pos[0]] = 'S'

                    # check if won
                    hit_counter = 0
                    for row in self.boards[self.opponent]:
                        hit_counter += row.count('S')
                    if hit_counter == 5:
                        win = True
                else:
                    self.sboards[self.opponent] = hit(
                        self.sboards[self.opponent], pos)

                    self.inf.label = 'Hit!'
                    self.inf.emoji = '🔥'
                    # await self.channel.send("Hit!", delete_after=5)
            else:
                # it is a miss
                self.sboards[self.opponent] = miss(
                    self.sboards[self.opponent], pos)

                self.player, self.opponent = self.opponent, self.player
                self.p, self.o = self.o, self.p

                self.inf.label = 'Miss!'
                self.inf.emoji = '❌'

                # await self.channel.send("Miss!", delete_after=5)

            # send image of board

            # file = combine_boards(
            #     self.opponent, self.player, self.o.name, self.p.name, self.opponent)

            # with open(file, "rb") as fh:
            #     image = discord.File(fh, filename=file)
            emb = discord.Embed(title='Battleship')
            emb.add_field(name=' ', inline=False,
                          value=self.sboards[self.opponent])
            emb.set_footer(text=f'Current Turn: {self.p.display_name}')

            if win:
                self.clear_items()
                emb.remove_footer()
                await self.message.edit(embed=emb, view=self)
                # await self.img.edit(attachments=[image])
                await self.channel.send(f'{self.p.mention} has won the battleship match against {self.o.mention}!')
                self.bo.end_game(self.player, self.opponent)
                return

            for child in self.children:
                child.disabled = False

            self.num = None
            self.alph = None
            await self.message.edit(embed=emb, view=self)

        else:
            await self.channel.send("You have already moved there.", delete_after=5)
            for child in self.children:
                child.disabled = False
            await self.message.edit(view=self)

    @discord.ui.button(label="Resign", style=discord.ButtonStyle.gray, row=4)
    async def surrender(self, interaction, button):
        for child in self.children:
            child.disabled = True

        b1 = Button(label="Confirm", style=discord.ButtonStyle.red, row=4)

        b2 = Button(label="Back", style=discord.ButtonStyle.grey, row=4)

        async def confirm_surr(interaction):
            self.p = await self.bo.client.fetch_user(self.player)
            self.o = await self.bo.client.fetch_user(self.opponent)
            await interaction.response.defer()
            self.clear_items()
            emb = discord.Embed(title='Battleship')
            emb.add_field(name=' ', inline=False,
                          value=self.sboards[self.opponent])            
            await self.message.edit(embed=emb, view=self)
            await self.channel.send(f'{self.p.mention} resigned!\n{self.o.mention} has won the battleship match against {self.p.mention}!')
            self.bo.end_game(self.opponent, self.player)
            return

        async def back(interaction):
            self.remove_item(b1)
            self.remove_item(b2)
            for child in self.children:
                child.disabled = False

            await interaction.response.edit_message(view=self)

        b1.callback = confirm_surr
        b2.callback = back
        self.add_item(b1)
        self.add_item(b2)

        await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction):
        if interaction.user.id != self.player:
            if interaction.user.id == self.opponent:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
            else:
                await interaction.response.send_message('You cannot use that!', ephemeral=True)
            return False
        else:
            return True


class Battleship(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.battles = []
        self.placed = {}

        self.states = {}
        self.boards = {}
        self.coords = {}
        # a = Value([False, 0, 591825462393569294])
        # {user_id:[battle_state,channel,current user turn]}
        self.battle_data = {}

    @app_commands.command(description="Challenge a user to a battleship match.")
    @commands.guild_only()
    async def battleship(self, interaction, opponent: Member = None):
        # await interaction.response.defer()

        if opponent.bot:
            await interaction.response.send_message('You cannot challenge a bot...', delete_after=5, ephemeral=True)
            return

        if opponent == interaction.user:
            await interaction.response.send_message('Specify another player, not yourself...',
                                                    delete_after=5, ephemeral=True)
            return

        if any(interaction.user.id in sublist for sublist in self.battles):
            await interaction.response.send_message('You are already in a battleship match!', ephemeral=True)
            return

        if any(opponent.id in sublist for sublist in self.battles):
            await interaction.response.send_message(
                'That user is already in a battleship match!', ephemeral=True)
            return

        view = InviteUser(opponent)
        await interaction.response.send_message(
            f'{opponent.mention}, you have been challenged to a battleship match by {interaction.user.mention}!',
            view=view
        )
        view.message = await interaction.original_response()

        res = await view.wait()

        if res:
            return
        else:
            if view.value:
                list = [opponent.id, interaction.user.id]
                fnames = []
                list.sort()
                self.battles.append(list)

                for user in list:
                    self.states[user] = False
                    with open('battleship/user_data/setups.json') as f:
                        json_data = json.load(f)
                        if str(user) in json_data:
                            self.placed[user] = [1, 2, 3, 4, 5]
                            self.coords[user] = {
                                int(value): json_data[f'{user}'][value] for value in json_data[f'{user}']}
                            self.boards[user] = coords_to_board(
                                self.coords[user])
                        else:
                            self.placed[user] = []
                            self.coords[user] = {}
                            self.boards[user] = [
                                [0 for x in range(SIZE)] for y in range(SIZE)]

                        msg = imager(self.coords[user])
                        fnames.append(msg)
                        # file = imager(self.coords[user], user)
                        # with open(file, "rb") as fh:
                        #     fnames.append(discord.File(fh, filename=file))

                player = random.choice(list)
                channel = interaction.channel
                data = Value([channel, player])
                self.battle_data[interaction.user.id] = data
                self.battle_data[opponent.id] = data
                
                emb = discord.Embed(title='BATTLESHIP:')
                emb.add_field(name=f'{interaction.user.display_name} vs {opponent.display_name}', inline=False, value="*Setup your battle layout in your DM's.*")

                await channel.send(embed=emb)

                # my_filename = 'battleship/images/spaceships2.png'
                # with open(my_filename, "rb") as fh:
                #     b = discord.File(fh, filename=my_filename)
                # with open(my_filename, "rb") as fh:
                #     b2 = discord.File(fh, filename=my_filename)

                if interaction.user.id == list[1]:
                    fnames = fnames[::-1]

                # msg = await interaction.user.send(file=fnames[0])
                # msg2 = await opponent.send(file=fnames[1])
                # await interaction.user.send(file=b)
                # await opponent.send(file=b2)
                emb = discord.Embed(title='Setup')
                emb.add_field(name=' ', value=fnames[0], inline=False)

                emb2 = discord.Embed(title='Setup')
                emb2.add_field(name=' ', value=fnames[1], inline=False)

                view = Place(self, interaction.user)
                view.message = await interaction.user.send(embed=emb, view=view)
                view2 = Place(self, opponent)
                view2.message = await opponent.send(embed=emb2, view=view2)

    async def begin(self, id, board, coords):
        self.states[id] = True
        self.boards[id] = board
        self.coords[id] = coords
        opponent = get_opponent(self.battles, id)

        if self.states[opponent] == True:
            player = self.battle_data[id].v[1]

            a = await self.client.fetch_user(player)
            opponent = opponent if player != opponent else id
            b = await self.client.fetch_user(opponent)

            # oname = b.name
            pname = a.display_name
            ab = imager({})

            emb = discord.Embed(title='Battleship')
            emb.add_field(
                name=f"{a.display_name}, {b.display_name}. Your battleship match has begun!", inline=False, value=ab)
            emb.set_footer(text=f'Current Turn: {pname}')

            view = Move(player, opponent, self)
            view.message = await self.battle_data[id].v[0].send(embed=emb, view=view)

    # @commands.command()
    # async def btest(self, ctx):
    #     arav = 591825462393569294
    #     zmbdy = 1157593866136981565
    #     self.battles = [[zmbdy, arav]]
    #     self.states = {zmbdy: True, arav: True}
    #     self.placed = {zmbdy: [1, 2, 3, 4, 5], arav: [1, 2, 3, 4, 5]}
    #     self.boards = {arav: [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [0, 'X', 'X', 'S', 0, 0, 0, 0, 0, 0],
    #                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [0, 'X', 'X', 'S', 0, 0, 0, 0, 0, 0],
    #                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [0, 'X', 'X', 'X', 'S', 0, 0, 0, 0, 0],
    #                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [0, 'X', 'X', 'X', 'X', 'S', 0, 0, 0, 0]],

    #                    zmbdy: [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                            [0, 1, 0, 'X', 0, 'X', 0, 'X', 0, 'X'],
    #                            [0, 1, 0, 'X', 0, 'X', 0, 'X', 0, 'X'],
    #                            [0, 0, 0, 'S', 0, 'S', 0, 'X', 0, 'X'],
    #                            [0, 0, 0, 0, 0, 0, 0, 'S', 0, 'X'],
    #                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 'S'],
    #                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]}
    #     self.coords = {arav: {1: [[1, 1], 'h'],
    #                           2: [[1, 3], 'h'],
    #                           3: [[1, 5], 'h'],
    #                           4: [[1, 7], 'h'],
    #                           5: [[1, 9], 'h']},
    #                    zmbdy: {1: [[1, 1], 'v'],
    #                            2: [[3, 1], 'v'],
    #                            3: [[5, 1], 'v'],
    #                            4: [[7, 1], 'v'],
    #                            5: [[9, 1], 'v']}}
    #     # {id:{item:[pos,orientation]}}
    #     a = Value([0, arav])
    #     self.battle_data = {
    #         arav: a,
    #         zmbdy: a
    #     }
    #     self.battle_data[arav].v[0] = ctx.channel
    #     await self.battle_data[arav].v[0].send("Your battleship match has begun!.")

    #     img = Image.open('battleship/images/background.jpg')
    #     img.save(f'battleship/user_data/{arav}-setup.png')
    #     img.save(f'battleship/user_data/{zmbdy}-setup.png')

    #     pname = 'arav7550'
    #     oname = 'test12bot'

    #     file = combine_boards(arav, zmbdy, pname, oname, arav)

    #     with open(file, "rb") as fh:
    #         image = discord.File(fh, filename=file)

    #     msg = await self.battle_data[arav].v[0].send(file=image)

    #     view = Move(arav, zmbdy, msg, self)
    #     view.message = await self.battle_data[arav].v[0].send(view=view)

    def end_game(self, winner, loser):
        list = [winner, loser]
        list.sort()
        del self.states[winner]
        del self.states[loser]
        del self.placed[winner]
        del self.placed[loser]
        del self.boards[winner]
        del self.boards[loser]
        del self.coords[winner]
        del self.coords[loser]
        del self.battle_data[winner]
        del self.battle_data[loser]

        self.battles.remove(list)


async def setup(client):
    await client.add_cog(Battleship(client))


def code_to_coords(code):
    coord = code[0] + str(SIZE - int(code[1:]))
    nums = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3,
        'E': 4,
        'F': 5,
        'G': 6,
        'H': 7,
        'I': 8
    }
    return [nums[coord[0]], int(coord[1:])]


def coords_to_board(coords, board=None):
    # {item: [[pos],ori]}
    if not board:
        board = [[0 for i in range(SIZE)] for j in range(SIZE)]
    coords = {int(value): coords[value] for value in coords}
    for item in coords:
        ori = coords[item][1]
        length = [2, 3, 3, 4, 5]
        pos = coords[item][0]
        item_length = length[item - 1]
        if ori == 'h':
            x = 1
            y = 0
        elif ori == 'v':
            x = 0
            y = 1

        for i in range(item_length):
            board[pos[1] + (y*i)][pos[0] + (x * i)] = item

    return board


def space_available(board, coord, item_length, orientation):
    if orientation == 'h':
        x = 1
        y = 0
        if coord[0] + item_length > SIZE:
            return False
    elif orientation == 'v':
        x = 0
        y = 1
        if coord[1] + item_length > SIZE:
            return False
    for i in range(item_length):
        if board[coord[1] + (y * i)][coord[0] + (x * i)] != 0:
            return False
    return True


def remove_item(board, item):
    for y in range(SIZE):
        for x in range(SIZE):
            if board[y][x] == item:
                board[y][x] = 0
    return board


def get_opponent(battles, id):
    for sublist in battles:
        if id in sublist:
            a = sublist.copy()
            a.remove(id)
            return a[0]


def get_pair(battles, id):
    for sublist in battles:
        if id in sublist:
            return sorted(sublist.copy())


def imager(items):
    alph = "🇦​🇧​🇨​🇩​🇪​🇫​🇬​🇭​🇮"

    num = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣"

    s = "⬛" + alph[:SIZE*2-1] + "⬛"
    l = s + '\n'
    for i in range(SIZE-1, -1, -1):
        l += num[i*3:i*3+3] + "🟦"*SIZE + num[i*3:i*3+3] + '\n'
    l += s

    d = [SIZE*2+5+i*(SIZE+7) for i in range(SIZE)]

    lg = [2, 3, 3, 4, 5]

    for item, [pos, ori] in items.items():
        item = int(item)

        ln = lg[item-1]
        if ori == 'h':
            s = d[pos[1]]+pos[0]
            l = l[:s] + '🚀'*ln + l[s+ln:]
        else:
            for i in range(ln):
                s = d[pos[1]+i]+pos[0]
                l = l[:s] + '🚀' + l[s+1:]

    return l


def miss(l, pos):
    d = [SIZE*2+5+i*(SIZE+7) for i in range(SIZE)]
    s = d[pos[1]]+pos[0]
    l = l[:s] + '❌' + l[s+1:]
    return l


def hit(l, pos):
    d = [SIZE*2+5+i*(SIZE+7) for i in range(SIZE)]
    s = d[pos[1]]+pos[0]
    l = l[:s] + '🔥' + l[s+1:]
    return l


def sink(l, pos, item, ori):
    d = [SIZE*2+5+i*(SIZE+7) for i in range(SIZE)]
    lg = [2, 3, 3, 4, 5]

    item = int(item)
    ln = lg[item-1]

    if ori == 'h':
        s = d[pos[1]]+pos[0]
        l = l[:s] + '💀'*ln + l[s+ln:]
    else:
        for i in range(ln):
            s = d[pos[1]+i]+pos[0]
            l = l[:s] + '💀' + l[s+1:]

    return l


def randomize():
    items = [(1, 2), (2, 3), (3, 3), (4, 4), (5, 5)]
    board = [[0 for x in range(SIZE)] for y in range(SIZE)]
    coords = {}
    for i in range(5):
        item, lnth = items.pop(random.randint(0, len(items)-1))
        ori = random.choice(['h', 'v'])
        x = random.randrange(0, SIZE)
        y = random.randrange(0, SIZE)
        while not space_available(board, [x, y], lnth, ori):
            ori = random.choice(['h', 'v'])
            x = random.randrange(0, SIZE)
            y = random.randrange(0, SIZE)

        coords[item] = [[x, y], ori]
        board = coords_to_board(coords, board)

    return coords, board
