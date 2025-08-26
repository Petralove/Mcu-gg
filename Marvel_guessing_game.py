import streamlit as st
import random

# A dictionary of Marvel characters and their hints
# The hints are listed from least to most revealing
CHARACTERS = {
    "Iron Man": [
        "I am a founding member of the Avengers.",
        "My alter ego is a billionaire, playboy, and genius inventor.",
        "My heart is powered by an Arc Reactor.",
        "I created a series of powerful armored suits to fight villains."
    ],
    "Captain America": [
        "I am the super-soldier from World War II.",
        "My shield is made of vibranium.",
        "I was frozen in ice for decades before being revived.",
        "My alter ego is Steve Rogers, a symbol of American patriotism."
    ],
    "Spider-Man": [
        "I was bitten by a radioactive spider.",
        "My powers include web-slinging and a 'spider-sense'.",
        "My alter ego is a high school student from Queens, New York.",
        "My main motto is 'With great power comes great responsibility'."
    ],
    "The Hulk": [
        "I turn into a green, powerful monster when I get angry.",
        "I was exposed to a high dose of gamma radiation.",
        "I have superhuman strength with no known upper limit.",
        "My alter ego is a brilliant scientist named Bruce Banner."
    ],
    "Captain Marvel": [
        "I was an air force pilot before I got my powers.",
        "My powers are from a fusion of human and alien DNA.",
        "I can fly and fire powerful energy blasts from my hands.",
        "My alter ego is Carol Danvers."
    ]
}

def initialize_game():
    """Initializes or resets the game state."""
    st.session_state.character = random.choice(list(CHARACTERS.keys()))
    st.session_state.hints_shown = 0
    st.session_state.game_over = False
    st.session_state.attempts = 0
    st.session_state.hint_message = ""

def main():
    """Main function to run the Streamlit app."""
    st.title("Guess the Marvel Character! 💥")

    # Initialize the game if it's not already running
    if 'character' not in st.session_state:
        initialize_game()

    if st.session_state.game_over:
        st.header("Game Over!")
        if st.session_state.attempts == 0:
            st.success(f"You guessed it right on the first try! The character was {st.session_state.character}.")
        else:
            st.success(f"You guessed it! The character was {st.session_state.character}. You took {st.session_state.attempts} attempt(s) and saw {st.session_state.hints_shown} hint(s).")
        if st.button("Play Again?"):
            initialize_game()
            st.experimental_rerun()
    else:
        st.write("I'm thinking of a Marvel character. Can you guess who it is?")

        # --- Game Hints Section ---
        st.markdown("---")
        if st.button("Give me a hint"):
            if st.session_state.hints_shown < len(CHARACTERS[st.session_state.character]):
                st.session_state.hints_shown += 1
                st.session_state.hint_message = CHARACTERS[st.session_state.character][st.session_state.hints_shown - 1]
            else:
                st.session_state.hint_message = "No more hints! You've seen them all."
        st.info(st.session_state.hint_message)
        st.markdown("---")
        
        # --- User Guess Section ---
        with st.form(key='guess_form'):
            guess = st.text_input("Enter your guess:", key="guess_input").strip()
            submitted = st.form_submit_button("Submit Guess")

            if submitted:
                st.session_state.attempts += 1
                if guess.lower() == st.session_state.character.lower():
                    st.session_state.game_over = True
                    st.success(f"Correct! You got it in {st.session_state.attempts} attempts.")
                    st.experimental_rerun()
                else:
                    st.warning("Incorrect. Try again!")

        st.write(f"Attempts: {st.session_state.attempts}")

        # Add a button to reset the game
        if st.button("Start a New Game"):
            initialize_game()
            st.experimental_rerun()


if __name__ == "__main__":
    main()
