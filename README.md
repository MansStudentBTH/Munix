# Munix
The idea for the project is about being able to play a user’s favourite songs directly from the console. This is for solving the common problem of having a lot of your favourite music unorganised and not easily manageable. With Munix the user is able to create playlists, add songs, play music and more. The main users of the program are music enjoyers and artists. With this media manager, you can easily manage your collection of music. The data was generated from this source: https://openai.com/blog/chatgpt. 

## Running the program
1. First, create the database with the SQL code from the SQL folder. Start with running the DatabaseINIT.sql then DatabaseInsert.sql and at last the DatabaseProcedures.sql. This has to be done manually in for example MySQL Workbench.
2. The next step is installing the required packages (preferably in a virtual environment) this is done through the pip install -r requirements.txt.
3. After downloading all required packages, run the main.py file from the base directory (i.e the directory in which main.py is stored).
4. Enjoy the worlds greatest and most innovative music player app!

(OBS! As of currently, you cannot play any real music, you can only see what it would look like playing a song)


## Commands
| Command | Description |
|---------|-------------|
| ls | Show directory (users/playlists/songs) |
| cd <directory_name> or ..  | change directory |
| mkuser <username>          | Create a user in the select user screen |
| mkplaylist <playilst_name> | Create a playlist |
| play <song_name>           | play a song |
| quit                       | exit application | 
| song <> or <song_name>     | If empty: Display all songs in database, else show info of song with name <song_name> |
| artist <> or <artist_name> | If empty: display all artists in database, else show artist and their albums |
| playing                    | Show the currently playing song |
| ishere <song_name>         | Check if song exists in playlist| 
| add <song_name>            | Add song to the playlist which the user is currently in |
| album <album_name>         | If multiple: Show all albums with the name <album_name>, else Show the album with all its songs |
| help                       | Show a list of available commands in the current screen |
| pause                      | Pause the music player |
| queue <> or <song_name>    | If empty: Show the queue, else queue a song with the name <song_name> |
| skip                       | Skip a song |
| prev                       | Play the previous song in the queue |
