import discord,random
import regex as re
from discord.ext import commands
from countdown.anscheck import posAns
from PIL import Image, ImageDraw, ImageFont

class Mathgame(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.goals = {}
        self.nums = {}
        

    @commands.command(description="Starts a mathgame round.")
    #@commands.has_permissions(administrator=True)
    async def mg(self, ctx):
      embmsg = discord.Embed(
        colour = discord.Colour.blue()
      )
      embmsg.set_footer(text='Use mgans <ans> to answer!')
      embmsg.set_author(name='Use these numbers to get to the target number!')
      if ctx.author.id not in self.nums or ctx.author.id not in self.goals:
        self.goals[ctx.author.id] = 'None'
      if self.goals[ctx.author.id] == 'None':
        self.nums[ctx.author.id] = GetNums()
        if self.nums[ctx.author.id]!='Invalid':
          self.goals[ctx.author.id] = target()
          while posAns(self.nums[ctx.author.id], self.goals[ctx.author.id])=='Invalid':
            self.goals[ctx.author.id] = target()
          numimage = numimager(self.nums[ctx.author.id], self.goals[ctx.author.id])
          embmsg.set_image(url="attachment://mathgame.png")
          await ctx.channel.send(file=discord.File(numimage), embed=embmsg)
      else:
        embed= discord.Embed(colour=discord.Colour.red())
        embed.add_field(name='Mathgame',value='You already ran this command!')
        await ctx.channel.send(embed=embed)
        return
    
    @commands.command(description="Answer the mathgame.", usage="<ans>")
    async def mgans(self, ctx, *answers):
      ans = ''
      for answer in answers:
        ans += answer
      print(ans)
      if self.goals[ctx.author.id] != 'None':
        numbers = self.nums[ctx.author.id]
        target = self.goals[ctx.author.id]
        answer = maths(ans, numbers, target)
        if answer=='Amazing':
          embed = discord.Embed(colour=discord.Color.green())
          embed.add_field(name='Mathgame', value='Well Done! \nThe answer is correct.')
          await ctx.channel.send(embed=embed)
          self.goals[ctx.author.id] = 'None'
          return
        else:
          embed = discord.Embed(colour = discord.Colour.red())
          embed.add_field(name='Mathgame', value='Incorrect!\nTry again.')
          await ctx.channel.send(embed=embed)
          return
      else:
        await ctx.channel.send("Pease run the mg command first.")
    
    @commands.command(description="Skips the current mathgame round.")
    async def mgskip(self, ctx):
      if self.goals[ctx.author.id] != 'None':
        embed = discord.Embed(colour=discord.Colour.purple())
        embed.set_footer(text="Skipped this round")
        answercheck = posAns(self.nums[ctx.author.id], self.goals[ctx.author.id])
        embed.add_field(name='Mathgame', value='Some possible answers:')
        n=1
        for real in answercheck:
          strn = str(n)+')'
          embed.add_field(name=strn, value=real)
          n+=1
        await ctx.channel.send(embed=embed)
        self.goals[ctx.author.id] = 'None'
        return
      else:
        await ctx.channel.send("Pease run the mg command first.")

async def setup(client):
    await client.add_cog(Mathgame(client))

def GetNums():
  owo= random.randrange(1,5)
  if owo==1:
     n1= random.randrange(25,101,25)
     n2= random.randrange(25,101,25)
     n3= random.randrange(1,11)
     n4= random.randrange(1,11)
     n5= random.randrange(1,11)
     n6= random.randrange(1,11)
     while n1==n2:
        n2= random.randrange(25,101,25)
     numbers=[n1,n2,n3,n4,n5,n6]
     return numbers
  elif owo==2:
     n1= random.randrange(25,101,25)
     n2= random.randrange(1,11)
     n3= random.randrange(1,11)
     n4= random.randrange(1,11)
     n5= random.randrange(1,11)
     n6= random.randrange(1,11)
     numbers=[n1,n2,n3,n4,n5,n6]
     return numbers
  elif owo==3:
     n1= random.randrange(25,101,25)
     n2= random.randrange(25,101,25)
     n3= random.randrange(25,101,25)
     n4= random.randrange(1,11)
     n5= random.randrange(1,11)
     n6= random.randrange(1,11)
     while n1==n2 or n1==n3 or n2==n3:
        if n1==n2:
           n2= random.randrange(25,101,25)
        elif n1==n3:
           n3= random.randrange(25,101,25)
        elif n2==n3:
           n3= random.randrange(25,101,25)
     numbers=[n1,n2,n3,n4,n5,n6]
     return numbers
  elif owo==4:
    n1= random.randrange(25,101,25)
    n2= random.randrange(25,101,25)
    n3= random.randrange(25,101,25)
    n4= random.randrange(25,101,25)
    n5= random.randrange(1,11)
    n6= random.randrange(1,11)
    while n1==n2 or n1==n3 or n1==n4 or n2==n3 or n2==n4 or n3==n4:
       if n1==n2:
          n2= random.randrange(25,101,25)
       elif n1==n3:
          n3= random.randrange(25,101,25)
       elif n1==n4:
          n4= random.randrange(25,101,25)
       elif n2==n3:
          n3= random.randrange(25,101,25)
       elif n2==n4:
          n4= random.randrange(25,101,25)
       elif n3==n4:
          n4= random.randrange(25,101,25)
  else:
    numbers= ('Invalid Difficulty')
    return numbers
  numbers=[str(n1),str(n2),str(n3),str(n4),str(n5),str(n6)]
  return numbers

def target():
  target = random.randrange(101,999)
  return target

def numimager(nums, goal):
  img = Image.open('countdown/testimage1.png')
  draw = ImageDraw.Draw(img)
  font1 = ImageFont.truetype('countdown/Calibri.ttf', 230)
  font2 = ImageFont.truetype('countdown/Calibri.ttf', 300)
  target = str(goal)
  draw.text((180,695),str(nums[0]),"white",font=font1)
  draw.text((795,695),str(nums[1]),"white",font=font1)
  draw.text((1393, 695),str(nums[2]),"white",font=font1)
  draw.text((180, 1025),str(nums[3]),"white",font=font1)
  draw.text((795, 1025),str(nums[4]),"white",font=font1)
  draw.text((1393, 1025),str(nums[5]),"white",font=font1)
  draw.text((765, 235),target,"white",font=font2)
  img.resize((350,240))
  img.save('countdown/mathgame.png')
  img.close
  return 'countdown/mathgame.png'


def replacer(eq):
     eq=eq.replace(' ', '')
     eq=eq.replace('÷','/')
     eq=eq.replace('x','*')
     eq=eq.replace('×','*')
     eq=eq.replace('^','**')
     return eq

def maths(math,numbers,target):
 n1= str(numbers[0])
 n2= str(numbers[1])
 n3= str(numbers[2])
 n4= str(numbers[3])
 n5= str(numbers[4])
 n6= str(numbers[5])
 math1= replacer(math)
 separator= ' '
 a= separator.join(re.split("[^0-9]*",math1))
 b= a.replace('  ',',')
 c= b.replace(' ','')
 d= c.split(',')
 nums= []
 for i in d:
    try:
        int(i)
        nums.append(i)
    except:
        pass
 outcome=None
 for n in nums:
   if n==(n1):
        n1= None
   elif n==(n2):
        n2= None
   elif n==(n3):
        n3= None
   elif n==(n4):
        n4= None
   elif n==(n5):
        n5= None
   elif n==(n6):
        n6= None
   else:
       outcome='Failed!'
       break
   outcome='success'
 if outcome==None:
     outcome='Failed!'
 try:
  evalint=int(eval(math1))
  if evalint==target and outcome=='success':
     return ('Amazing')
  else:
     return ('Failed!')
 except:
  return ('Failed!')

  