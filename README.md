# KokoAI-Discord-Chatbot
A starter discord chatbot that uses OpenAI API's model to respond to user's inputs from discord.

<br>
<br>
<br>

# Installing Dependencies
1. Make sure to have the following installed prior:
    - `python 3.12.6 +`
    - `pip 24.2 +`
2. Create a virtual environment to isolate different Python projects
    - **MacOS:**
    ```
        python3 -m venv <venv_name>  
    ```

    - **Windows:**
    ```
        python -m venv <venv_name>
    ```
3. Activate the virtual environment
   - **MacOS:**
    ```
        source location\of\venv_name\activate
    ```
   - **Windows:**
    ```
        location\of\venv_name\activate
    ```
4. Install the dependencies needed in `requirements.txt`
    - **MacOS:**
    ```
        pip3 install -r requirements.txt
    ```
    - **Windows:**
    ```
        pip install -r requirements.txt
    ```



<br>
<br>
<br>

# Running The Program
1. Make sure you have set up your own `.env` file with the following tokens
   - `DISCORD_TOKEN` - can get one by signing up in Discord For Developers
   - `OPENAI_API_KEY` - can get one by paying from OpenAI
   - `PERSONALITY_PROMPT` - create your own bot's personality (up to you how you want your chatbot to be)
2. Run the program
    ```
    python(3) main.py
    ```

<br>
<br>
<br>

# Quitting The Program
1. Type `quit` or `exit` to quit the program.
2. Make sure to deactivate the virtual environment by typing and entering the command in current virtual environment terminal
    ```
        deactivate
    ```

<br>
<br>

# Versions
## Version 1
- [x] Simple input gathering and API request calls to OpenAI API.  
- [x] Done through command line.

## Version 2
- [x] Discord bot integration - Gets input from users who mentions or replies to the bot.
- [x] Local hosting

## Version 2.1
- [ ] Able to store message contexts 
- [ ] Able to be hosted on a remote server to be online 
