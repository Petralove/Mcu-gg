import streamlit as st
import random

# A dictionary of Marvel characters with hints.
# This serves as our game's "database".
MARVEL_CHARACTERS = {
    "Iron Man": [
        "I am a genius, billionaire, playboy, philanthropist.",
        "My suit is powered by an arc reactor.",
        "I am the leader of the Avengers and often referred to as 'Tony'."
    ],
    "Captain America": [
        "I am a super-soldier from World War II.",
        "My primary weapon is a vibranium shield.",
        "I was frozen in ice for decades before being revived."
    ],
    "Hulk": [
        "When I get angry, I transform into a giant green monster.",
        "I am a brilliant scientist named Bruce Banner.",
        "My catchphrase is 'Hulk Smash!'"
    ],
    "Thor": [
        "I am a prince from Asgard, often called the God of Thunder.",
        "My primary weapon is a powerful hammer, Mjolnir.",
        "I have a brother named Loki."
    ],
    "Black Widow": [
        "I am a highly skilled spy and assassin.",
        "I have a red-colored hair.",
        "I am a founding member of the Avengers, but I don't have superpowers."
    ],
    "Spider-Man": [
        "My powers come from a radioactive spider bite.",
        "I can shoot webs from my wrists.",
        "My alter-ego is Peter Parker."
    ],
    "Black Panther": [
        "I am the king and protector of the fictional African nation of Wakanda.",
        "My suit is made of vibranium.",
        "I have a sister named Shuri."
    ],
    "Doctor Strange": [
        "I am a Master of the Mystic Arts.",
        "I was a brilliant surgeon before my accident.",
        "My cloak has a life of its own."
    ],
    "Ant-Man": [
        "I can shrink to the size of an ant and also become a giant.",
        "My suit is made by Dr. Hank Pym.",
        "My alter-ego is Scott Lang."
    ],
    "Captain Marvel": [
        "I was a U.S. Air Force pilot.",
        "I can fly and shoot energy blasts from my hands.",
        "My real name is Carol Danvers."
    ],
    "Wolverine": [
        "I have adamantium claws and an incredible healing factor.",
        "I am part of the X-Men.",
        "My real name is Logan."
    ],
    "Deadpool": [
        "I am a merc with a mouth and I know I'm in a comic book.",
        "I have an incredible healing factor.",
        "My alter-ego is Wade Wilson."
    ]
}

def reset_game():
    """Resets the game state to its initial values."""
    st.session_state.game_state = "not_started"
    st.session_state.tries_left = 15
    st.session_state.hints_given = 0
    st.session_state.secret_character = None
    st.session_state.computer_guesses = []
    st.session_state.current_hint_index = 0
    st.session_state.computer_turn_state = "making_guess"
    st.session_state.last_user_hint = ""
    st.session_state.user_question_history = []
    st.session_state.questions_asked = 0
    st.session_state.user_guess_input_val = ""

def start_game():
    """Initializes the game and chooses a character."""
    st.session_state.game_state = "in_progress"
    st.session_state.secret_character = random.choice(list(MARVEL_CHARACTERS.keys()))

def user_guesses_mode():
    """Handles the game logic when the user is guessing."""
    st.subheader("Guess the Marvel Character")
    
    st.write(f"Tries left: {st.session_state.tries_left}")
    
    # Give a new hint every 5 tries
    if st.session_state.tries_left % 5 == 0 and st.session_state.tries_left < 15 and st.session_state.current_hint_index < 3:
        st.info(f"Hint {st.session_state.current_hint_index + 1}: {MARVEL_CHARACTERS[st.session_state.secret_character][st.session_state.current_hint_index]}")
        st.session_state.current_hint_index += 1

    # Question and Answer section
    if st.session_state.questions_asked < 20:
        st.write(f"Ask a question to help you guess! ({20 - st.session_state.questions_asked} questions remaining)")
        user_question = st.text_input("Your question:", key="user_question_input")
        
        if st.button("Ask Question"):
            if user_question:
                st.session_state.questions_asked += 1
                # Simple keyword-based logic to answer the question
                found = any(word.lower() in ' '.join(MARVEL_CHARACTERS[st.session_state.secret_character]).lower() for word in user_question.split())
                answer = "Yes" if found else "No"
                st.session_state.user_question_history.append((user_question, answer))
    else:
        st.warning("You have used all 20 questions! You can no longer ask for hints.")

    # Display the history of questions and answers
    if st.session_state.user_question_history:
        for q, a in st.session_state.user_question_history:
            if a == "Yes":
                st.success(f"You asked: '{q}' -> **Yes**")
            else:
                st.error(f"You asked: '{q}' -> **No**")

    st.markdown("---")

    # Guessing section
    st.markdown("### Make Your Guess")
    st.write("Enter the character's name to guess.")
    user_guess = st.text_input("Your guess:", value=st.session_state.user_guess_input_val, key="user_guess_input")
    
    if st.button("Submit Guess"):
        st.session_state.tries_left -= 1
        st.session_state.user_guess_input_val = ""
        
        if user_guess.lower() == st.session_state.secret_character.lower():
            st.session_state.game_state = "win"
            st.balloons()
        elif st.session_state.tries_left <= 0:
            st.session_state.game_state = "lose"
        else:
            st.error("Incorrect guess. Try again!")

def computer_guesses_mode():
    """Handles the game logic when the computer is guessing."""
    st.subheader("The Computer is Guessing")

    # The user gives a hint to the computer every 5 tries.
    if st.session_state.tries_left % 5 == 0 and st.session_state.tries_left < 15 and st.session_state.current_hint_index < 3:
        user_hint = st.text_input(f"The computer has made {15 - st.session_state.tries_left} guesses. Give it a hint:")
        st.session_state.current_hint_index += 1
        st.session_state.last_user_hint = user_hint
    elif st.session_state.current_hint_index > 0:
        st.info(f"Last hint you gave: '{st.session_state.last_user_hint}'")

    if st.session_state.computer_turn_state == "making_guess":
        if st.button("Computer, Make a Guess!", key="computer_guess_button"):
            st.session_state.tries_left -= 1
            st.session_state.computer_guess_this_turn = random.choice(list(MARVEL_CHARACTERS.keys()))
            st.session_state.computer_guesses.append(st.session_state.computer_guess_this_turn)
            st.session_state.computer_turn_state = "waiting_for_feedback"
    elif st.session_state.computer_turn_state == "waiting_for_feedback":
        st.write(f"The computer guesses: **{st.session_state.computer_guess_this_turn}**")
        st.warning("Please tell the computer if the guess is correct or not.")
        is_correct = st.radio("Is this your character?", ("Yes", "No"), key="user_feedback_radio")

        if st.button("Confirm Feedback", key="confirm_feedback_button"):
            if is_correct == "Yes":
                st.session_state.game_state = "win"
            elif st.session_state.tries_left <= 0:
                st.session_state.game_state = "lose"
            else:
                st.session_state.computer_turn_state = "making_guess"

    st.write(f"Tries left: {st.session_state.tries_left}")
    st.markdown("---")
    st.write("Computer's past guesses:")
    for guess in st.session_state.computer_guesses:
        st.write(f"- {guess}")

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Marvel Guessing Game", layout="centered")

    st.title("Guess the Marvel Character")
    st.markdown("---")

    # Initialize session state variables if they don't exist
    if "game_state" not in st.session_state:
        reset_game()
    
    # Mode selection and game start
    if st.session_state.game_state == "not_started":
        st.write("Welcome to the Marvel Guessing Game! Choose your role.")
        game_mode = st.radio("Choose a game mode:", ["I'll guess", "The computer will guess"])
        
        if st.button("Start Game"):
            st.session_state.game_mode = game_mode
            start_game()
    
    elif st.session_state.game_state == "in_progress":
        if st.session_state.game_mode == "I'll guess":
            user_guesses_mode()
        else:
            computer_guesses_mode()

    elif st.session_state.game_state == "win":
        st.success(f"You win! The character was **{st.session_state.secret_character}**.")
        st.button("Play Again", on_click=reset_game)

    elif st.session_state.game_state == "lose":
        st.error(f"You lose! The character was **{st.session_state.secret_character}**.")
        st.button("Play Again", on_click=reset_game)

if __name__ == "__main__":
    main()
