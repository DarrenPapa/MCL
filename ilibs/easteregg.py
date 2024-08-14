# For the "Cat Easter Egg" Nyan!

from random import choice

messages = (
    "Good luck on programming!",
    "Hi how are you, Thanksu I am gudo.",
    "Oh May Gah!!!",
    "Nyan!",
    "Watashi wa neko desu.",
    "Anime wa yasashii desu!",
    "2020 to 2024 is a mess!",
    "Tiktok is full of sh*t.",
    "Demon slayer? Ghibli movies? Spritied Away :3",
    "Tiktok ist schieße!",
    "Anime ist sehr net!",
    "Ich heiße Katze.",
    "MCL ist weder gut noch schlecht."
)

message = choice(messages)

print_cat = lambda x=None: print(f"""
 |\\_/| ,
=(OwO)=|  [ The cat of truth ]
 |   |/
 |---|
The Cat Says...
{message if not x else x}""")

if __name__ == "__main__":
    print_cat()