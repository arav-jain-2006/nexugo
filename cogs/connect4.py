import discord
from discord.ext import commands
from discord import Member, app_commands
from discord.ui import View, Button
import random


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
        await interaction.response.send_message("Connect-4 challenge accepted!")
        await interaction.message.edit(view=self)
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button_callback(self, interaction, button):
        for child in self.children:
            child.disabled = True
        await interaction.response.send_message("Connect-4 challenge declined!")
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


class Move(View):
    def __init__(self, player, opponent, p, o, board, channel, c4o):
        super().__init__(timeout=None)
        self.player = player
        self.opponent = opponent
        self.board = board
        self.p, self.o = p, o
        self.colour = 1
        self.c4o = c4o
        self.channel = channel

        nums = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

        for n, i in enumerate(nums):
            b = Button(label=i, custom_id=str(n+1),
                       style=discord.ButtonStyle.blurple)
            b.callback = self.num_callback
            self.add_item(b)

    async def num_callback(self, interaction):
        await interaction.response.defer()

        self.num = interaction.data['custom_id']

        self.board = add(self.colour, int(self.num), self.board)

        c = {1: "🔴", 2: "🟡"}

        emb = discord.Embed(title='Connect 4')
        emb.add_field(name='', inline=False, value=imager(self.board))
        emb.set_footer(
            text=f'Current Turn: {self.o.display_name} {c[3-self.colour]}')

        if check_win(self.board, self.colour):
            self.clear_items()
            emb.remove_footer()
            await self.message.edit(view=self, embed=emb)
            await self.channel.send(f'{self.p.mention} has won the connect-4 game against {self.o.mention}!')
            self.c4o.end_game(self.player, self.opponent)
            return

        self.colour = 3 - self.colour
        self.opponent, self.player = self.player, self.opponent
        self.o, self.p = self.p, self.o

        for child in self.children:
            if child.custom_id == self.num and not space_available(self.board, int(self.num)):
                child.disabled = True

        await self.message.edit(view=self, embed=emb)

    @discord.ui.button(label="Resign", style=discord.ButtonStyle.gray, row=2)
    async def surrender(self, interaction, button):
        for child in self.children:
            child.disabled = True

        b1 = Button(label="Confirm", style=discord.ButtonStyle.red, row=3)

        b2 = Button(label="Back", style=discord.ButtonStyle.grey, row=3)

        async def confirm_surr(interaction):
            await interaction.response.defer()
            self.clear_items()
            emb = discord.Embed(title='Connect 4')
            emb.add_field(name=' ', inline=False, value=imager(self.board))
            await self.message.edit(embed=emb, view=self)
            await self.channel.send(f'{self.p.mention} resigned!\n{self.o.mention} has won the connect-4 game against {self.p.mention}!')
            self.c4o.end_game(self.opponent, self.player)
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


class Value:
    def __init__(self, v=None):
        self.v = v


class Connect4(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.battles = []

    @app_commands.command(description="Challenge a user to a connect-4 game.")
    @commands.guild_only()
    async def connect4(self, interaction, opponent: Member = None):
        # await interaction.response.defer()
        if opponent.bot:
            await interaction.response.send_message('You cannot challenge a bot...', delete_after=5, ephemeral=True)
            return

        if opponent == interaction.user:
            await interaction.response.send_message('Specify another player, not yourself...',
                                                    delete_after=5, ephemeral=True)
            return

        if any(interaction.user.id in sublist for sublist in self.battles):
            await interaction.response.send_message('You are already in a connect-4 game!', ephemeral=True)
            return

        if any(opponent.id in sublist for sublist in self.battles):
            await interaction.response.send_message(
                'That user is already in a connect-4 game!', ephemeral=True)
            return

        view = InviteUser(opponent)
        await interaction.response.send_message(
            f'{opponent.mention}, you have been challenged to a connect-4 game by {interaction.user.mention}!',
            view=view
        )
        view.message = await interaction.original_response()

        res = await view.wait()

        if res or not view.value:
            return

        list = [opponent.id, interaction.user.id]
        list.sort()
        self.battles.append(list)

        board = [[0 for x in range(7)] for i in range(6)]

        player = random.choice(list)

        emb = discord.Embed(title='Connect 4')
        emb.add_field(name='', inline=False, value=imager(board))

        opp = opponent.id if player != opponent.id else interaction.user.id

        p = await self.client.fetch_user(player)
        o = await self.client.fetch_user(opp)

        emb.set_footer(text=f'Current Turn: {p} 🔴')

        view = Move(player, opp, p, o, board, interaction.channel, self)

        view.message = await interaction.channel.send(embed=emb, view=view)

    def end_game(self, winner, loser):
        list = [winner, loser]
        list.sort()

        self.battles.remove(list)


async def setup(client):
    await client.add_cog(Connect4(client))


def imager(board):
    l = ''
    for y in board:
        l += "🟦"
        for x in y:
            if x == 1:
                l += "🔴"
            elif x == 2:
                l += "🟡"
            else:
                l += "⬛"
        l += "🟦\n"
    l += "🔻1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣🔻"
    return l


def space_available(board, num):
    if board[0][num-1] != 0:
        return False
    return True


def add(colour, num, board):
    for i in range(-1, -7, -1):
        if board[i][num-1] == 0:
            board[i][num-1] = colour
            return board


def check_win(board, num):
    l = [num]*4
    # check horizontal
    for i in range(6):
        for j in range(4):
            if board[i][j:j+4] == l:
                return True

    # check vertical
    for i in range(7):
        for j in range(3):
            if [board[j+x][i] for x in range(4)] == l:
                return True

    # check diagonals
    for i in range(3):
        for j in range(4):
            if [board[i+x][j+x] for x in range(4)] == l:
                return True
            elif [board[5-i-x][j+x] for x in range(4)] == l:
                return True

    return False
