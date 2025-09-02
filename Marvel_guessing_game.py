import streamlit as st
import random
import time

# A dictionary of Marvel characters with hints and structured traits.
# Traits are now in a dictionary for more reliable computer guessing.
MARVEL_CHARACTERS = {
    "Iron Man": {
        "hints": [
            "I am a genius, billionaire, playboy, philanthropist.",
            "My suit is powered by an arc reactor.",
            "I am the leader of the Avengers and often referred to as 'Tony'."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": True,
            "is_human": True,
            "is_genius": True,
            "uses_special_weapon": True,
            "has_healing_factor": False
        }
    },
    "Captain America": {
        "hints": [
            "I am a super-soldier from World War II.",
            "My primary weapon is a vibranium shield.",
            "I was frozen in ice for decades before being revived."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": True,
            "is_super_soldier": True,
            "is_human": True,
            "uses_special_weapon": True,
            "has_healing_factor": False
        }
    },
    "Hulk": {
        "hints": [
            "When I get angry, I transform into a giant green monster.",
            "I am a brilliant scientist named Bruce Banner.",
            "My catchphrase is 'Hulk Smash!'"
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": True,
            "is_green": True,
            "is_human": True,
            "uses_special_weapon": False,
            "has_healing_factor": True
        }
    },
    "Thor": {
        "hints": [
            "I am a prince from Asgard, often called the God of Thunder.",
            "My primary weapon is a powerful hammer, Mjolnir.",
            "I have a brother named Loki."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": True,
            "is_god": True,
            "uses_special_weapon": True,
            "has_healing_factor": False
        }
    },
    "Black Widow": {
        "hints": [
            "I am a highly skilled spy and assassin.",
            "I have a red-colored hair.",
            "I am a founding member of the Avengers, but I don't have superpowers."
        ],
        "traits": {
            "is_male": False,
            "is_hero": True,
            "is_avenger": True,
            "is_human": True,
            "uses_special_weapon": False,
            "has_healing_factor": False
        }
    },
    "Spider-Man": {
        "hints": [
            "My powers come from a radioactive spider bite.",
            "I can shoot webs from my wrists.",
            "My alter-ego is Peter Parker."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": False, # He is often an ally, but not always a core Avenger
            "is_human": True,
            "uses_special_weapon": False,
            "has_healing_factor": True
        }
    },
    "Black Panther": {
        "hints": [
            "I am the king and protector of the fictional African nation of Wakanda.",
            "My suit is made of vibranium.",
            "I have a sister named Shuri."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": True,
            "is_king": True,
            "is_human": True,
            "uses_special_weapon": False,
            "has_healing_factor": False
        }
    },
    "Doctor Strange": {
        "hints": [
            "I am a Master of the Mystic Arts.",
            "I was a brilliant surgeon before my accident.",
            "My cloak has a life of its own."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": True,
            "is_sorcerer": True,
            "is_human": True,
            "uses_special_weapon": False,
            "has_healing_factor": False
        }
    },
    "Ant-Man": {
        "hints": [
            "I can shrink to the size of an ant and also become a giant.",
            "My suit is made by Dr. Hank Pym.",
            "My alter-ego is Scott Lang."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": True,
            "is_human": True,
            "uses_special_weapon": False,
            "has_healing_factor": False
        }
    },
    "Captain Marvel": {
        "hints": [
            "I was a U.S. Air Force pilot.",
            "I can fly and shoot energy blasts from my hands.",
            "My real name is Carol Danvers."
        ],
        "traits": {
            "is_male": False,
            "is_hero": True,
            "is_avenger": True,
            "is_human": False, # Kree DNA
            "uses_special_weapon": False,
            "has_healing_factor": False
        }
    },
    "Wolverine": {
        "hints": [
            "I have adamantium claws and an incredible healing factor.",
            "I am part of the X-Men.",
            "My real name is Logan."
        ],
        "traits": {
            "is_male": True,
            "is_hero": True,
            "is_avenger": False,
            "is_mutant": True,
            "is_human": False,
            "uses_special_weapon": True,
            "has_healing_factor": True
        }
    },
    "Deadpool": {
        "hints": [
            "I am a merc with a mouth and I know I'm in a comic book.",
            "I have an incredible healing factor.",
            "My alter-ego is Wade Wilson."
        ],
        "traits": {
            "is_male": True,
            "is_hero": False, # Anti-hero
            "is_avenger": False,
            "is_human": True,
            "uses_special_weapon": True,
            "has_healing_factor": True
        }
    }
}

# Questions for the computer to ask, mapped to the new traits
COMPUTER_QUESTIONS = {
    "is_male": "Is your character a male?",
    "is_avenger": "Is your character an Avenger?",
    "is_hero": "Is your character a hero?",
    "uses_special_weapon": "Does your character use a special weapon?",
    "has_healing_factor": "Does your character have a healing factor?",
    "is_human": "Is your character human?",
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
    st.session_state.possible_characters = list(MARVEL_CHARACTERS.keys())
    st.session_state.question_asked_this_turn = None
    st.session_state.computer_questions_asked = 0
    st.session_state.computer_question_history = []
    st.session_state.computer_guess_made = False

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
        st.info(f"Hint {st.session_state.current_hint_index + 1}: {MARVEL_CHARACTERS[st.session_state.secret_character]['hints'][st.session_state.current_hint_index]}")
        st.session_state.current_hint_index += 1

    # Question and Answer section
    st.markdown("### Ask Questions")
    if st.session_state.questions_asked < 20:
        st.write(f"Use this box to ask questions and get 'Yes' or 'No' answers. ({20 - st.session_state.questions_asked} questions remaining)")
        user_question = st.text_input("Your question:", key="user_question_input")
        
        if st.button("Ask Question"):
            if user_question:
                st.session_state.questions_asked += 1
                # Simple keyword-based logic to answer the question
                found = any(word.lower() in ' '.join(MARVEL_CHARACTERS[st.session_state.secret_character]['hints']).lower() for word in user_question.split())
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
    st.markdown("### Make Your Final Guess")
    st.write("Enter the character's full name to guess.")
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
    """Handles the game logic when the computer is guessing by asking questions."""
    st.subheader("The Computer is Guessing")
    
    # Check if a guess can be made
    if st.session_state.computer_guess_made:
        st.info(f"The computer's final guess is: **{st.session_state.computer_guess_made}**")
        st.button("Continue", on_click=lambda: st.session_state.update(computer_guess_made=False))
        return

    if st.session_state.computer_questions_asked >= 15:
        st.session_state.game_state = "lose"
        st.error(f"The computer has run out of questions and loses!")
        return

    st.write(f"Questions asked: {st.session_state.computer_questions_asked}/15")
    
    # Check if the computer has enough info to make a guess
    if len(st.session_state.possible_characters) == 1:
        computer_guess = st.session_state.possible_characters[0]
        st.session_state.computer_guess_made = computer_guess
        if computer_guess.lower() == st.session_state.secret_character.lower():
            st.session_state.game_state = "win"
            st.balloons()
        else:
            st.session_state.game_state = "lose"
        return
    else:
        # Computer asks a question
        available_questions = [key for key in COMPUTER_QUESTIONS.keys() if key not in [q[0] for q in st.session_state.computer_question_history]]
        if not available_questions:
            st.session_state.game_state = "lose"
            st.error("The computer is out of unique questions and loses!")
            return
        
        question_key = random.choice(available_questions)
        st.session_state.question_asked_this_turn = question_key
        st.info(f"The computer asks: **{COMPUTER_QUESTIONS[question_key]}**")
        
        user_answer = st.radio("Your answer:", ("Yes", "No"), key="user_answer_radio")
        
        if st.button("Submit Answer"):
            st.session_state.computer_questions_asked += 1
            st.session_state.computer_question_history.append((question_key, user_answer))
            
            # Update the list of possible characters based on the answer
            new_possible_characters = []
            
            for char_name in st.session_state.possible_characters:
                char_traits = MARVEL_CHARACTERS[char_name]['traits']
                
                # Check if the character's trait matches the question and answer
                if (user_answer == "Yes" and char_traits.get(question_key) is True) or \
                   (user_answer == "No" and char_traits.get(question_key) is False):
                    new_possible_characters.append(char_name)

            st.session_state.possible_characters = new_possible_characters
            st.write(f"Possible characters remaining: {len(st.session_state.possible_characters)}")

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
            with st.spinner('Starting game...'):
                time.sleep(1)
            st.session_state.game_mode = game_mode
            start_game()
    
    elif st.session_state.game_state == "in_progress":
        if st.session_state.game_mode == "I'll guess":
            user_guesses_mode()
        else:
            computer_guesses_mode()
            
        # Display the computer's question history log
        st.markdown("---")
        st.markdown("### Computer's Question Log")
        if st.session_state.computer_question_history:
            for q_key, answer in st.session_state.computer_question_history:
                st.write(f"- Computer asked: '{COMPUTER_QUESTIONS[q_key]}'")
                st.write(f"  Your answer: **{answer}**")

    elif st.session_state.game_state == "win":
        char_image_url = f"https://placehold.co/300x300/F0F2F6/262730?text={st.session_state.secret_character.replace(' ', '+')}"
        
        if st.session_state.game_mode == "I'll guess":
            st.success(f"You win! The character was **{st.session_state.secret_character}**.")
            st.image(char_image_url, caption=st.session_state.secret_character)
        else:
            st.success(f"The computer wins! The character was **{st.session_state.secret_character}**.")
            st.image(char_image_url, caption=st.session_state.secret_character)

        st.button("Play Again", on_click=reset_game)

    elif st.session_state.game_state == "lose":
        char_image_url = f"https://placehold.co/300x300/F0F2F6/262730?text={st.session_state.secret_character.replace(' ', '+')}"
        
        if st.session_state.game_mode == "I'll guess":
            st.error(f"You lose! The character was **{st.session_state.secret_character}**.")
            st.image(char_image_url, caption=st.session_state.secret_character)
        else:
            st.error(f"The computer loses! The character was **{st.session_state.secret_character}**.")
            st.image(char_image_url, caption=st.session_state.secret_character)
            
        st.button("Play Again", on_click=reset_game)

if __name__ == "__main__":
    main()
