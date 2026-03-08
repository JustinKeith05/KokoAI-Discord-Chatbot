# Feature Logs

## Speech Feature
### Problems
1. Wrong Object (`Message` vs `Context`)
    ```
    'Message' object has no attribute 'send'
    ```
    | Object | Where it comes from | What it can do |
    | --- | --- | --- | 
    | `Context (ctx)` | command functions (!join) | Sends messages |
    | `Message` | `on_message` event | Represents a received message

    ```
    # We were calling
    await speak_text(message, response)

    # But the function used
    await message.send(..)

    ```
    - Messages are data objects, NOT channels

    **Fix**
    ```
    await message.channel.send(...)
    ```
2. Discord Voice Dependency (`davey`)
    ```
    Runtime Error: davey library needed in order to use voice
    ```
    - Used to use `PyNaCl` but newer `discord.py` version require `davey`
