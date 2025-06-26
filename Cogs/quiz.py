import discord
from discord import Embed, Color, ButtonStyle, SelectOption
from discord.ext import commands
from discord.ui import View, Button, Select
import csv
import asyncio
import datetime
import time


LOG_CHANNEL = 777042897630789633
QUIZ_LOGS = 903139993646682113
TMOD_ROLE = 714891905392967691
ADMIN_ROLE = 470547452873932806

quiz_questions = []
quiz_file = "Trial_Moderator_Quiz.csv"
# quiz_file = "short_quiz.csv"

with open(quiz_file, "r") as file:
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
        self.bot = None  # Store bot reference for cleanup
        self.interface_type = None  # 'buttons' or 'select'
        self.start_message = None

class QuizView(View):
    def __init__(self, quiz_session, question_index):
        super().__init__(timeout=300)
        self.quiz_session = quiz_session
        self.question_index = question_index
        self.user_selections = []
        # Start timing when view is created
        self.quiz_session.question_start_time = time.time()

        options = self.quiz_session.quiz_data.get_options(question_index)

        if self.quiz_session.interface_type == "select":
            # Add select menu for options
            select_options = []
            for i, option in enumerate(options):
                select_options.append(SelectOption(
                    label=option,
                    value=chr(65+i),  # A, B, C, D
                    description=f"Option {chr(65+i)}"
                ))

            select_menu = Select(
                placeholder="Select your answer(s)...",
                options=select_options,
                min_values=0,
                max_values=len(select_options),
                custom_id="quiz_select"
            )
            select_menu.callback = self.select_callback
            self.add_item(select_menu)
        else:
            # Add option buttons (A, B, C, D)
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

    async def select_callback(self, interaction):
        if interaction.user != self.quiz_session.user:
            await interaction.response.send_message("This quiz is not for you!", ephemeral=True)
            return

        self.user_selections = interaction.data['values']

        # Update placeholder to show selections
        select_menu = self.children[0]  # First child is the select menu
        if self.user_selections:
            select_menu.placeholder = f"Selected: {', '.join(self.user_selections)}"
        else:
            select_menu.placeholder = "Select your answer(s)..."

        await interaction.response.edit_message(view=self)

    async def submit_callback(self, interaction):
        if interaction.user != self.quiz_session.user:
            await interaction.response.send_message("This quiz is not for you!", ephemeral=True)
            return
        await interaction.channel.typing()
        # Calculate time taken
        time_taken = time.time() - self.quiz_session.question_start_time
        self.quiz_session.question_times.append(time_taken)

        # Store user answer
        self.quiz_session.user_answers.append(self.user_selections.copy())

        # Check if correct and calculate partial credit
        correct_answers = self.quiz_session.quiz_data.get_correct_answers(self.question_index)
        is_correct = set(self.user_selections) == set(correct_answers)

        # Calculate partial credit with penalty for wrong answers
        all_options = self.quiz_session.quiz_data.get_options(self.question_index)
        correct_set = set(correct_answers)
        user_set = set(self.user_selections)
        all_options_set = set(all_options)

        # Calculate correct ratio
        correct_selected = len(correct_set & user_set)
        total_correct = len(correct_set)
        correct_ratio = correct_selected / total_correct if total_correct > 0 else 0

        # Calculate penalty for incorrect selections
        incorrect_selected = len(user_set - correct_set)
        total_incorrect = len(all_options_set - correct_set)
        incorrect_penalty = incorrect_selected / total_incorrect if total_incorrect > 0 else 0

        # Final score with penalty, floored at 0
        partial_score = max(0, correct_ratio - incorrect_penalty)
        self.quiz_session.score += partial_score

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
        # Calculate partial credit for display
        all_options = self.quiz_session.quiz_data.get_options(self.question_index)
        correct_set = set(correct_answers)
        user_set = set(self.user_selections)
        all_options_set = set(all_options)

        # Calculate correct ratio
        correct_selected = len(correct_set & user_set)
        total_correct = len(correct_set)
        correct_ratio = correct_selected / total_correct if total_correct > 0 else 0

        # Calculate penalty for incorrect selections
        incorrect_selected = len(user_set - correct_set)
        total_incorrect = len(all_options_set - correct_set)
        incorrect_penalty = incorrect_selected / total_incorrect if total_incorrect > 0 else 0

        # Final score with penalty, floored at 0
        partial_score = max(0, correct_ratio - incorrect_penalty)

        if is_correct:
            result_text = "✅ Correct!"
        elif partial_score > 0:
            result_text = f"🟡 Partial Credit: {partial_score:.2f}"
        else:
            result_text = "❌ Incorrect"

        embed.add_field(name="Result", value=result_text, inline=False)

        # Disable all components
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
            description=f"Final Score: {self.quiz_session.score:.2f}/{self.quiz_session.total_questions}",
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

        # Clean up bot messages before showing results
        await self.cleanup_messages()

        # Send results message
        await self.quiz_session.channel.send(embed=embed)

        # Log detailed results to QUIZ_LOGS channel
        await self.log_quiz_results()

    async def log_quiz_results(self):
        """Log detailed quiz results to QUIZ_LOGS channel"""
        try:
            if not self.quiz_session.bot:
                return

            log_channel = self.quiz_session.bot.get_channel(QUIZ_LOGS)
            if not log_channel:
                return

            percentage = (self.quiz_session.score / self.quiz_session.total_questions) * 100
            total_time = sum(self.quiz_session.question_times)

            # Create main results embed
            main_embed = Embed(
                title="Quiz Results",
                description=f"**User:** {self.quiz_session.user.mention}\n**Score:** {self.quiz_session.score}/{self.quiz_session.total_questions} ({percentage:.1f}%)\n**Total Time:** {total_time:.1f}s",
                color=Color.green() if percentage >= 80 else Color.red(),
                timestamp=datetime.datetime.now()
            )
            await log_channel.send(embed=main_embed)

            # Split question details across multiple messages if needed
            question_chunks = []
            current_chunk = ""

            for i in range(self.quiz_session.total_questions):
                question = self.quiz_session.quiz_data.get_question(i)
                user_answer = ", ".join(self.quiz_session.user_answers[i]) if self.quiz_session.user_answers[i] else "None"
                correct_answer = ", ".join(self.quiz_session.quiz_data.get_correct_answers(i))
                is_correct = set(self.quiz_session.user_answers[i]) == set(self.quiz_session.quiz_data.get_correct_answers(i))
                time_taken = self.quiz_session.question_times[i]

                status = "✅" if is_correct else "❌"
                question_text = f"**Q{i+1}:** {status} ({time_taken:.1f}s)\n"
                question_text += f"*{question[:100]}{'...' if len(question) > 100 else ''}*\n"
                question_text += f"**Your Answer:** {user_answer}\n"
                question_text += f"**Correct:** {correct_answer}\n\n"

                # Check if adding this question would exceed 1800 chars (safe margin)
                if len(current_chunk) + len(question_text) > 1800:
                    question_chunks.append(current_chunk)
                    current_chunk = question_text
                else:
                    current_chunk += question_text

            # Add final chunk if not empty
            if current_chunk:
                question_chunks.append(current_chunk)

            # Send question details in separate embeds
            for i, chunk in enumerate(question_chunks):
                chunk_embed = Embed(
                    title=f"Question Details ({i+1}/{len(question_chunks)})" if len(question_chunks) > 1 else "Question Details",
                    description=chunk,
                    color=Color.blue()
                )
                await log_channel.send(embed=chunk_embed)

        except Exception as e:
            print(f"Error logging quiz results: {e}")

    async def cleanup_messages(self):
        """Purge bot messages from the channel"""
        try:
            if self.quiz_session.bot:
                def is_bot_message(message):
                    return message.author == self.quiz_session.bot.user
                if self.quiz_session.start_message is not None:
                    await self.quiz_session.channel.purge(limit=100, check=is_bot_message, after=self.quiz_session.start_message)
                else:
                    await self.quiz_session.channel.purge(limit=len(quiz_questions), check=is_bot_message)

        except Exception as e:
            print(f"Error cleaning up messages: {e}")

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

class InterfaceChoiceView(View):
    def __init__(self, user, bot, channel):
        super().__init__(timeout=60)
        self.user = user
        self.bot = bot
        self.channel = channel

    @discord.ui.button(label="Buttons", style=ButtonStyle.primary, emoji="🔘")
    async def buttons_choice(self, interaction, button):
        if interaction.user != self.user:
            await interaction.response.send_message("This quiz is not for you!", ephemeral=True)
            return

        message = await interaction.response.edit_message(content=f"{self.user.mention}, starting quiz with buttons! Each question has 1-3 valid answers. Select all correct answers and no incorrect ones for credit. Good luck!", view=None)
        await self.start_quiz_with_interface("buttons", message)

    @discord.ui.button(label="Select Menu", style=ButtonStyle.primary, emoji="📋")
    async def select_choice(self, interaction, button):
        if interaction.user != self.user:
            await interaction.response.send_message("This quiz is not for you!", ephemeral=True)
            return

        message = await interaction.response.edit_message(content=f"{self.user.mention}, starting quiz with select menus! Each question has 1-3 valid answers. Select all correct answers and no incorrect ones for credit. Good luck!", view=None)
        await self.start_quiz_with_interface("select", message)

    async def start_quiz_with_interface(self, interface_type, start_message):
        print(f"Quiz started for {self.user.name} with {interface_type}!")

        # Log the quiz start
        try:
            log_channel = self.bot.get_channel(LOG_CHANNEL)
            if log_channel:
                embed = Embed(title="Logged Event:", description=f"Quiz started for {self.user.name} with {interface_type}!", color=Color.green(), timestamp=datetime.datetime.now())
                await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging quiz start: {e}")

        # Initialize quiz
        quiz_data = quizQuestions()
        quiz_session = QuizSession(self.user, self.channel, quiz_data)
        quiz_session.bot = self.bot
        quiz_session.interface_type = interface_type
        quiz_session.start_message = start_message

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

    @commands.command(name='start_quiz', aliases=['quiz'], help='Have a target do a quiz!')
    @commands.has_guild_permissions(administrator=True)
    async def start_quiz(self, ctx, target_mod=None):
        await ctx.message.delete()
        try:
            if target_mod is None:
                # Default to the author if not specified
                target_mod = ctx.author.id
            # Handle both mentions and raw IDs
            if isinstance(target_mod, str):
                # Remove mention formatting if present
                user_id = target_mod.strip('<@!>')
                user = await self.bot.fetch_user(int(user_id))
            else:
                user = await self.bot.fetch_user(target_mod)
            assert user is not None

        except AssertionError:
            await ctx.send("You must specify a target user.")
            return

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            return

        # Let user choose interface type
        interface_view = InterfaceChoiceView(user, self.bot, ctx.channel)
        await ctx.send(f"{user.mention}, it's quiz time! Choose your preferred interface:", view=interface_view)

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
