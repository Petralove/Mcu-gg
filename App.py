# This script creates a Marvel character guessing game using Streamlit and the Google Gemini API.
# The game has two modes:
# 1. You Guess: The AI thinks of a Marvel character, and you try to guess it.
# 2. AI Guesses: You think of a Marvel character, and the AI tries to guess it by asking you questions.

# --- Library Imports ---
import streamlit as st
import google.generativeai as genai
import random
import asyncio
import nest_asyncio
import re

# Apply the nest_asyncio patch to allow the use of asyncio.run in Streamlit.
nest_asyncio.apply()

# --- Gemini API Configuration ---
# Set your Google API key.
# It's recommended to store this in Streamlit secrets rather than hardcoding.
# For demonstration purposes, a placeholder is used here.
# st.secrets["GEMINI_API_KEY"]
GOOGLE_API_KEY = "AIzaSyCsFXdklVEGwiaj5D__1ex5UFiLtEsy96E"# Replace with your actual key if not using Streamlit secrets.
if not GOOGLE_API_KEY:
    try:
        GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    except:
        st.error("API Key not found. Please set it in Streamlit secrets.")
        st.stop()

# Configure the Gemini API.
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# --- Character and Game Data ---
# Define a list of Marvel characters with their attributes for each difficulty level.
# This serves as the "knowledge base" for the AI and the game logic.
MARVEL_CHARACTERS = {
    "Easy": [
        {"name": "Spider-Man", "attributes": ["male", "human", "super-strength", "super-agility", "web-shooter", "new-york", "avenger", "hero"]},
        {"name": "Iron Man", "attributes": ["male", "human", "genius", "powered-suit", "avenger", "hero", "billionaire", "weaponry"]},
        {"name": "Captain America", "attributes": ["male", "human", "super-strength", "super-soldier", "avenger", "hero", "shield", "world-war-2"]},
        {"name": "Hulk", "attributes": ["male", "human-like", "super-strength", "scientist", "monster", "avenger", "hero", "gamma-radiation"]},
    ],
    "Medium": [
        {"name": "Thor", "attributes": ["male", "asgardian", "god", "super-strength", "hammer", "avenger", "hero", "lightning"]},
        {"name": "Black Widow", "attributes": ["female", "human", "spy", "super-agility", "avenger", "hero", "agent", "russia"]},
        {"name": "Doctor Strange", "attributes": ["male", "human", "magic", "sorcerer", "avenger", "hero", "doctor", "new-york"]},
        {"name": "Black Panther", "attributes": ["male", "human", "super-strength", "king", "avenger", "hero", "wakanda", "vibranium"]},
        {"name": "Loki", "attributes": ["male", "asgardian", "god", "magic", "villain", "trickster", "thor's-brother"]},
        {"name": "Thanos", "attributes": ["male", "alien", "super-strength", "villain", "gauntlet", "infinity-stones"]},
    ],
    "Hard": [
        {"name": "Scarlet Witch", "attributes": ["female", "mutant", "magic", "reality-warping", "avenger", "hero", "chaos-magic"]},
        {"name": "Vision", "attributes": ["male", "robot", "super-strength", "avenger", "hero", "android", "mind-stone"]},
        {"name": "Ant-Man", "attributes": ["male", "human", "shrinking", "ant-control", "avenger", "hero", "ex-con"]},
        {"name": "The Wasp", "attributes": ["female", "human", "shrinking", "avenger", "hero", "wings", "stings"]},
        {"name": "Winter Soldier", "attributes": ["male", "human", "super-strength", "assassin", "anti-hero", "metal-arm", "world-war-2"]},
        {"name": "Nebula", "attributes": ["female", "cyborg", "villain", "avenger", "assassin", "thanos-daughter"]},
    ]
}

# --- Game Functions ---

def _initialize_session_state():
    """Initializes all necessary session state variables for the game."""
    if "game_mode" not in st.session_state:
        st.session_state.game_mode = "You Guess"
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Easy"
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "secret_character" not in st.session_state:
        st.session_state.secret_character = ""
    if "game_active" not in st.session_state:
        st.session_state.game_active = False
    if "guesses_left" not in st.session_state:
        st.session_state.guesses_left = 5
    if "ai_known_attributes" not in st.session_state:
        st.session_state.ai_known_attributes = []
    if "ai_question" not in st.session_state:
        st.session_state.ai_question = ""
    if "ai_possible_characters" not in st.session_state:
        st.session_state.ai_possible_characters = []
    if "first_turn" not in st.session_state:
        st.session_state.first_turn = True

def _new_game():
    """Resets the game state and starts a new game based on selected mode."""
    st.session_state.game_active = True
    st.session_state.conversation_history = []
    st.session_state.guesses_left = 5
    st.session_state.ai_known_attributes = []
    st.session_state.first_turn = True

    # Initialize state for AI Guesses mode
    if st.session_state.game_mode == "AI Guesses":
        st.session_state.ai_possible_characters = MARVEL_CHARACTERS[st.session_state.difficulty].copy()
        asyncio.run(_generate_ai_question_and_guess())
        st.session_state.conversation_history.append({"role": "assistant", "content": st.session_state.ai_question})
        
    # Initialize state for You Guess mode
    else:
        st.session_state.secret_character = random.choice(MARVEL_CHARACTERS[st.session_state.difficulty])
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": f"I've picked a character from the **{st.session_state.difficulty}** list. You have {st.session_state.guesses_left} chances to guess who I am! What's your first question?"}
        )

def _display_chat():
    """Displays the entire conversation history in the chat UI."""
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Asynchronous API Call Functions ---

async def _get_gemini_response(prompt):
    """Makes an asynchronous call to the Gemini API."""
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

async def _get_gemini_yes_no(question, character_name, character_attributes):
    """Asks the API to provide a yes/no answer for a character based on its attributes."""
    prompt = (
        f"You are a helpful assistant. I have a character named {character_name}. "
        f"The character's key attributes are: {', '.join(character_attributes)}. "
        f"Based on these attributes, please answer the following question with only 'Yes' or 'No'. "
        f"If the answer is 'No', also provide a brief, simple reason. "
        f"Question: '{question}'"
    )
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

async def _generate_ai_question_and_guess():
    """Generates the AI's next question or guess in AI Guesses mode."""
    if len(st.session_state.ai_possible_characters) <= 1:
        st.session_state.ai_question = "I think I know who it is. Can I make my final guess?"
        return

    known_attributes = st.session_state.ai_known_attributes
    prompt_context = f"So far, I know the character is: {', '.join(known_attributes)}. " if known_attributes else ""
    character_names = ', '.join([c['name'] for c in st.session_state.ai_possible_characters])

    prompt = (
        f"I am playing a 20-questions game. The possible characters are: {character_names}. "
        f"{prompt_context} "
        "Ask a single yes/no question to narrow down the possible characters. "
        "The question must be about a character's powers, abilities, or affiliations (e.g., 'Is the character a member of the Avengers?'). "
        "Do not ask about gender, species, or hair color unless you have already narrowed down the options. "
        "Start your response with 'Is the character...'. Do not ask a question that has already been asked."
    )
    
    response = await _get_gemini_response(prompt)
    st.session_state.ai_question = response

def _handle_ai_guess_response(user_answer):
    """Processes the user's yes/no answer in AI Guesses mode."""
    # Append user's response to conversation history.
    user_message = {"role": "user", "content": user_answer}
    st.session_state.conversation_history.append(user_message)
    
    # Check if the AI has asked for a final guess.
    if "Can I make my final guess?" in st.session_state.ai_question:
        if user_answer == "Yes":
            final_guess = random.choice(st.session_state.ai_possible_characters)
            st.session_state.conversation_history.append({"role": "assistant", "content": f"My final guess is **{final_guess['name']}**!"})
            st.session_state.game_active = False
            return
        else:
            st.session_state.conversation_history.append({"role": "assistant", "content": "Darn! Okay, let me ask another question."})
            asyncio.run(_generate_ai_question_and_guess())
            st.session_state.conversation_history.append({"role": "assistant", "content": st.session_state.ai_question})
            return

    # Process the user's yes/no answer to the AI's question.
    question_text = st.session_state.ai_question
    if user_answer == "Yes":
        # AI's question often contains the attribute itself (e.g., "is a member of the avengers").
        # We need to extract that attribute.
        question_words = question_text.lower().split()
        if "avenger" in question_words or "avengers" in question_words:
            attribute_to_check = "avenger"
        elif "asgardian" in question_words:
            attribute_to_check = "asgardian"
        elif "super-strength" in question_words:
            attribute_to_check = "super-strength"
        elif "human" in question_words:
            attribute_to_check = "human"
        elif "magic" in question_words:
            attribute_to_check = "magic"
        elif "female" in question_words:
            attribute_to_check = "female"
        elif "male" in question_words:
            attribute_to_check = "male"
        else:
            # Fallback for complex questions, the AI will just have to filter based on its own
            # interpretation of the response.
            st.session_state.conversation_history.append({"role": "assistant", "content": "Great, thanks! Let me think."})
            asyncio.run(_generate_ai_question_and_guess())
            st.session_state.conversation_history.append({"role": "assistant", "content": st.session_state.ai_question})
            return

        # Filter the possible characters based on the positive answer.
        st.session_state.ai_known_attributes.append(attribute_to_check)
        st.session_state.ai_possible_characters = [
            char for char in st.session_state.ai_possible_characters if attribute_to_check in char['attributes']
        ]

    else: # User answered "No"
        st.session_state.conversation_history.append({"role": "assistant", "content": "Okay, thanks! I'll keep that in mind."})
        # Filtering is tricky here, so we'll let the next AI question handle it.
        # Simple removal based on a hardcoded list of attributes won't work well
        # if the AI generates a complex question.

    # Generate the next AI question.
    asyncio.run(_generate_ai_question_and_guess())
    st.session_state.conversation_history.append({"role": "assistant", "content": st.session_state.ai_question})

def _handle_human_guess(user_guess):
    """Processes the user's guess in You Guess mode."""
    st.session_state.guesses_left -= 1
    guess_cleaned = user_guess.strip().lower()

    if guess_cleaned == st.session_state.secret_character['name'].lower():
        st.session_state.conversation_history.append({"role": "assistant", "content": f"That's right! The character was **{st.session_state.secret_character['name']}**! You win!"})
        st.session_state.game_active = False
    elif st.session_state.guesses_left > 0:
        st.session_state.conversation_history.append({"role": "assistant", "content": f"Nope, that's not me. You have {st.session_state.guesses_left} guesses left. Try another question!"})
    else:
        st.session_state.conversation_history.append({"role": "assistant", "content": f"You're out of guesses! The character was **{st.session_state.secret_character['name']}**. Better luck next time!"})
        st.session_state.game_active = False

def _handle_human_question(question_text):
    """Processes the user's yes/no question in You Guess mode."""
    # Get the AI's response asynchronously.
    response_text = asyncio.run(_get_gemini_yes_no(question_text, st.session_state.secret_character['name'], st.session_state.secret_character['attributes']))
    st.session_state.conversation_history.append({"role": "assistant", "content": response_text})

# --- Streamlit App UI ---

# Initialize session state on app load.
_initialize_session_state()

st.title("Guess the Marvel Character")
st.markdown("I'm thinking of a Marvel character. Can you guess who it is?")

# Sidebar for game settings
with st.sidebar:
    st.header("Game Settings")
    st.session_state.game_mode = st.radio(
        "Choose Game Mode:",
        options=["You Guess", "AI Guesses"],
        help="In 'You Guess' mode, you ask questions. In 'AI Guesses' mode, you answer questions."
    )

    st.session_state.difficulty = st.selectbox(
        "Select Difficulty:",
        options=["Easy", "Medium", "Hard"],
        index=0,
        help="Easy: 4 characters, Medium: 6 characters, Hard: 6 characters"
    )

    if st.button("New Game", type="primary"):
        _new_game()
        st.rerun()

# --- Main Game Loop and UI ---
if not st.session_state.game_active:
    st.info("Start a new game using the 'New Game' button in the sidebar!")
else:
    # Display the game's message board
    _display_chat()

    if st.session_state.game_mode == "You Guess":
        if st.session_state.game_active:
            # User input for questions and guesses
            prompt = st.chat_input("Ask a yes/no question or guess the character (e.g., 'Is the character male?' or 'Is the character Thor?')")
            if prompt:
                # Add user message to history
                user_message = {"role": "user", "content": prompt}
                st.session_state.conversation_history.append(user_message)

                # Differentiate between a question and a guess
                is_guess = any(char['name'].lower() in prompt.lower() for char in MARVEL_CHARACTERS[st.session_state.difficulty])
                if "guess" in prompt.lower() or is_guess:
                    _handle_human_guess(prompt)
                else:
                    _handle_human_question(prompt)
                st.rerun()

    else: # AI Guesses mode
        if st.session_state.game_active:
            st.markdown("I'll ask the questions, you just have to answer!")
            
            # The AI's last question is stored and displayed. Now the user needs to respond.
            if "I think I know who it is." in st.session_state.ai_question:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key="final_guess_yes"):
                        _handle_ai_guess_response("Yes")
                        st.rerun()
                with col2:
                    if st.button("No", key="final_guess_no"):
                        _handle_ai_guess_response("No")
                        st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key="answer_yes"):
                        _handle_ai_guess_response("Yes")
                        st.rerun()
                with col2:
                    if st.button("No", key="answer_no"):
                        _handle_ai_guess_response("No")
                        st.rerun()

# End of code block marker
