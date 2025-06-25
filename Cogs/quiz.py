from discord import Embed, Color, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
import csv
import asyncio
import datetime
import time


LOG_CHANNEL = 777042897630789633
TMOD_ROLE = 714891905392967691
ADMIN_ROLE = 470547452873932806
quiz_questions = []

with open("Trial_Moderator_Quiz.csv", "r") as file:
    reader = csv.reader(file)
    quiz_questions = list(reader)

class QuizSession:
    def __init__(self, user, channel, quiz_data):
        self.user = user
        self.channel = channel
        self.quiz_data = quiz_data
        self.current_question = 0
        self.user_answers = []
        self.score = 0
        self.total_questions = len(quiz_data.questions)
        self.question_times = []
        self.question_start_time = None

class QuizView(View):
    def __init__(self, quiz_session, question_index):
        super().__init__(timeout=300)
        self.quiz_session = quiz_session
        self.question_index = question_index
        self.user_selections = []
        # Start timing when view is created
        self.quiz_session.question_start_time = time.time()

        # Add option buttons (A, B, C, D)
        options = self.quiz_session.quiz_data.get_options(question_index)
        for i, option in enumerate(options):
            button = Button(
                label=option[0],  # A, B, C, D
                style=ButtonStyle.secondary,
                custom_id=f"option_{chr(65+i)}"
            )
            button.callback = self.option_callback
            self.add_item(button)

        # Add submit button
        submit_btn = Button(label="Submit", style=ButtonStyle.primary, custom_id="submit")
        submit_btn.callback = self.submit_callback
        self.add_item(submit_btn)

    async def option_callback(self, interaction):
        if interaction.user != self.quiz_session.user:
            await interaction.response.send_message("This quiz is not for you!", ephemeral=True)
            return

        option_letter = interaction.data['custom_id'].split('_')[1]

        if option_letter in self.user_selections:
            self.user_selections.remove(option_letter)
        else:
            self.user_selections.append(option_letter)

        # Update button styles
        for item in self.children[:-1]:  # Exclude submit button
            if item.custom_id.endswith(option_letter):
                item.style = ButtonStyle.success if option_letter in self.user_selections else ButtonStyle.secondary

        await interaction.response.edit_message(view=self)

    async def submit_callback(self, interaction):
        if interaction.user != self.quiz_session.user:
            await interaction.response.send_message("This quiz is not for you!", ephemeral=True)
            return

        # Calculate time taken
        time_taken = time.time() - self.quiz_session.question_start_time
        self.quiz_session.question_times.append(time_taken)

        # Store user answer
        self.quiz_session.user_answers.append(self.user_selections.copy())

        # Check if correct
        correct_answers = self.quiz_session.quiz_data.get_correct_answers(self.question_index)
        is_correct = set(self.user_selections) == set(correct_answers)
        if is_correct:
            self.quiz_session.score += 1

        # Show results embed
        await self.show_results(interaction, correct_answers, is_correct, time_taken)

    async def show_results(self, interaction, correct_answers, is_correct, time_taken):
        question = self.quiz_session.quiz_data.get_question(self.question_index)
        options = self.quiz_session.quiz_data.get_options(self.question_index)

        embed = Embed(
            title=f"Question {self.question_index + 1} Results",
            description=question,
            color=Color.green() if is_correct else Color.red()
        )

        options_text = "\n".join(options)
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.add_field(name="Your Answer", value=", ".join(self.user_selections) if self.user_selections else "None", inline=True)
        embed.add_field(name="Correct Answer", value=", ".join(correct_answers), inline=True)
        embed.add_field(name="Time Taken", value=f"{time_taken:.1f}s", inline=True)
        embed.add_field(name="Result", value="✅ Correct!" if is_correct else "❌ Incorrect", inline=False)

        # Disable all buttons
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

        # Move to next question after delay
        await asyncio.sleep(3)
        await self.next_question()

    async def next_question(self):
        self.quiz_session.current_question += 1

        if self.quiz_session.current_question >= self.quiz_session.total_questions:
            await self.show_final_results()
        else:
            await self.show_question(self.quiz_session.current_question)

    async def show_question(self, question_index):
        question = self.quiz_session.quiz_data.get_question(question_index)
        options = self.quiz_session.quiz_data.get_options(question_index)

        embed = Embed(
            title=f"Question {question_index + 1}/{self.quiz_session.total_questions}",
            description=question,
            color=Color.blue()
        )

        options_text = "\n".join(options)
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.set_footer(text="Select your answer(s) and click Submit")

        new_view = QuizView(self.quiz_session, question_index)
        await self.quiz_session.channel.send(embed=embed, view=new_view)

    async def show_final_results(self):
        embed = Embed(
            title="Quiz Complete!",
            description=f"Final Score: {self.quiz_session.score}/{self.quiz_session.total_questions}",
            color=Color.gold()
        )

        percentage = (self.quiz_session.score / self.quiz_session.total_questions) * 100
        total_time = sum(self.quiz_session.question_times)
        avg_time = total_time / len(self.quiz_session.question_times) if self.quiz_session.question_times else 0

        embed.add_field(name="Percentage", value=f"{percentage:.1f}%", inline=True)
        embed.add_field(name="Total Time", value=f"{total_time:.1f}s", inline=True)
        embed.add_field(name="Average Time", value=f"{avg_time:.1f}s", inline=True)

        if percentage >= 80:
            embed.add_field(name="Result", value="🎉 Passed!", inline=True)
        else:
            embed.add_field(name="Result", value="📚 Needs Review", inline=True)

        await self.quiz_session.channel.send(embed=embed)

class quizQuestions():
    def __init__(self):
        self.questions = []
        self.options = []  # Changed from answers to options for clarity
        self.correct_answers = []

        # Skip header row, process quiz data
        for row in quiz_questions[1:]:
            if len(row) >= 3:
                self.questions.append(row[0])
                # Split options by comma, strip whitespace
                self.options.append([opt.strip() for opt in row[1].split(',')])
                # Split correct answers by comma, strip whitespace
                self.correct_answers.append([ans.strip() for ans in row[2].split(',')])

    def get_question(self, index):
        return self.questions[index]

    def get_options(self, index):
        return self.options[index]

    def get_correct_answers(self, index):
        return self.correct_answers[index]

class Quiz(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.description = 'Quiz those trial mods!'

    async def log0101(self, message, title=None):
      print('logging event')
      cha = await self.bot.fetch_channel(LOG_CHANNEL)
      if not title:
        title="Logged Event:"
      embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime.now())
      await cha.send(embed=embed3)

    # events
    @commands.Cog.listener()
    async def on_ready(self):
      print('Quiz is online')

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def start_quiz(self, ctx, target_mod):
        # await ctx.message.delete()
        try:
            # Handle both mentions and raw IDs
            if isinstance(target_mod, str):
                # Remove mention formatting if present
                user_id = target_mod.strip('<@!>')
                user = await self.bot.fetch_user(int(user_id))
            else:
                user = await self.bot.fetch_user(target_mod)

            if user == None:
                await ctx.send("User not found in server.", delete_after=5)
                print("Failed to find user.")
                return
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            return

        await ctx.send(f"{user.mention}, it's quiz time! Each question has 1-3 valid answers. Select all correct answers and no incorrect ones for credit. Good luck!")
        print(f"Quiz started for {user.name}!")
        await self.log0101(f"Quiz started for {user.name}!")

        # Initialize quiz
        quiz_data = quizQuestions()
        quiz_session = QuizSession(user, ctx.channel, quiz_data)

        # Start first question
        await self.show_first_question(quiz_session)

    async def show_first_question(self, quiz_session):
        question = quiz_session.quiz_data.get_question(0)
        options = quiz_session.quiz_data.get_options(0)

        embed = Embed(
            title=f"Question 1/{quiz_session.total_questions}",
            description=question,
            color=Color.blue()
        )

        options_text = "\n".join(options)
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.set_footer(text="Select your answer(s) and click Submit")

        view = QuizView(quiz_session, 0)
        await quiz_session.channel.send(embed=embed, view=view)




async def setup(bot):
  await bot.add_cog(Quiz(bot))

if __name__ == "__main__":
    print("Quiz is running")
    quiz = quizQuestions()
    print(f"Q1: {quiz.get_question(0)}\n{quiz.get_options(0)}\n{quiz.get_correct_answers(0)}")
