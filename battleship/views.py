import discord
from discord.ext import commands
from discord import Member
from discord.ui import Button, View

class InviteUser(View):
    def __init__(self, ctx, member):
      super().__init__(timeout=60)
      self.ctx = ctx
      self.member = member
      self.value = False
      
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button_callback(self, button, interaction):
      # await interaction.response.send_message("Hello!")
      for child in self.children:
            child.disabled = True
      self.value = True
      await interaction.response.send_message("Battleship challenge accepted!")
      await self.message.edit(view=self)
      self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button_callback(self, button, interaction):
      for child in self.children:
        child.disabled = True
      await interaction.response.send_message("Battleship challenge declined!")
      await self.message.edit(view=self)
      self.stop()
      
    async def on_timeout(self):
      for child in self.children:
            child.disabled = True
      await self.message.edit(content="The request has timed out...", view=self)
      return

    async def interaction_check(self, interaction) -> bool:
      if interaction.user != self.member:
        await interaction.response.send_message("You cannot use that!", ephemeral=True)
        return False
      else:
        return True
        

class Place(View):
  
    def __init__(self, ctx):
      super().__init__(timeout=None)
      self.ctx = ctx
      
      self.item = None
      self.letter = None
      self.number = None
      self.orientation = None

      self.alphabets = ["A","B","C","D","E","F","G","H","I","J"]
      #numbers = ["1️⃣","2️⃣","3️⃣","5️⃣","4️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
      for i in range(5):
        button = Button(label=str(i+1),style=discord.ButtonStyle.blurple, custom_id=str(i+1))
        button.callback = self.item_callback
        self.add_item(button)
      # elif i==1:
      #   button = self.add_item(Button(label=alphabets[j],row=i))
      #   #button.callback = self.button_callback
      # elif i==2:
      #   button = self.add_item(Button(label=alphabets[j+5],row=i))
      #   #button.callback = self.button_callback
      # elif i==3:
      #   button= self.add_item(Button(label=str(j+1),row=i))
      #   #button.callback = self.button_callback 
      # elif i==4:
      #   button = self.add_item(Button(label=str(j+6),row=i))
      #   #button.callback = self.button_callback

    async def item_callback(self, interaction):
      #print(vars(interaction))
      self.reset()
      print(interaction.data)
      self.item = interaction.custom_id
      self.clear_items()
      for i in range(10):
        button = Button(label=self.alphabets[i], custom_id=self.alphabets[i])
        button.callback = self.letter_callback
        self.add_item(button)
      for i in range(10):
        button = Button(label=str(i+1), custom_id=str(i+1))
        button.callback = self.number_callback
        self.add_item(button)

      button = Button(label="Horizontal", style=discord.ButtonStyle.blurple, custom_id="h")
      button.callback = self.orientation_callback
      self.add_item(button)

      button = Button(label="Vertical", style=discord.ButtonStyle.blurple, custom_id="v")
      button.callback = self.orientation_callback
      self.add_item(button)
      #await interaction.response.send_message("hi!")
      await interaction.response.edit_message(view=self)
      

    async def letter_callback(self, interaction):
      self.letter = interaction.custom_id
      #await interaction.response.send_message("hi!")
      await interaction.response.edit_message(view=self)

    async def number_callback(self, interaction):
      self.number = interaction.custom_id
      #await interaction.response.send_message("hi!")
      await interaction.response.edit_message(view=self)

    async def orientation_callback(self, interaction):
      self.orientation = interaction.custom_id
      await interaction.response.edit_message(view=self)

    async def complete(self):
      pass
      
    def reset(self):
      self.item = None
      self.letter = None
      self.number = None
      self.orientation = None
  
      