import requests
from bs4 import BeautifulSoup as soup
import re
import os
import argparse
from tqdm import tqdm


def scrape(_title, contenttype, path):
    """
    Scrapes movie/tv show scripts from springfieldspringfield.co.uk/
    and stores them in textfiles in a new directory in the given path.
    """
    baselink = "https://www.springfieldspringfield.co.uk/"

    if contenttype == "tv":
        tssite = baselink + "episode_scripts.php?tv-show="
        tssite += _title
        # retrieve script sites
        ereq = requests.get(tssite)
        s_e = soup(ereq.content, 'html.parser')
        links = [a['href'] for
                 a in s_e.find_all('a', class_="season-episode-title")]
        episodetitles = [re.search(r"s\d\de\d\d", link).group() for link in
                         links]

        if len(episodetitles) != 0:
            os.chdir(path)
            # creates directory for the scripts if one doesn't exist already
            tsdir = f"{_title}_transscripts"
            if not os.path.exists(tsdir):
                os.makedirs(tsdir)
            # iterate over episodes, visual feedback with tqdm
            for title, link in tqdm(zip(episodetitles, links),
                                    total=len(links)):
                # create file and write episode script
                with open(f"{tsdir}/{title}.txt", "w+") as f:
                    ep = requests.get(baselink +
                                      link)
                    s_ep = soup(ep.content, "html.parser")
                    texts = s_ep.find_all('div',
                                          class_='scrolling-script-container')
                    for t in texts:
                        text = t.get_text()
                        f.write(text.lstrip())
            print("\nDone!\n")
        else:
            raise Exception

    elif contenttype == "m":
        tssite = baselink + "movie_script.php?movie="
        tssite += _title

        mreq = requests.get(tssite)
        movie = soup(mreq.content, 'html.parser')
        texts = movie.find_all('div', class_='scrolling-script-container')

        with open(f"{tsdir}/{_title}.txt", "w+") as f:
            for t in texts:
                mtext = t.get_text()
                f.write(mtext.lstrip())
        print("\nDone!\n")

    else:
        print(f"{contenttype} is not a valid type.")
        print("Use m for a movie and tv for a tv show.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    titledescription = """
    The title of the tv show/movie.
    Replace the spaces by -
    """
    parser.add_argument("title", help=titledescription)
    parser.add_argument("type", help="m for movie, tv for tv show.")
    parser.add_argument("path", nargs='?', default=os.getcwd())
    args = parser.parse_args()
    try:
        scrape(args.title, args.type, args.path)
    except:
        print("""\nNo transscripts found. Try adding the year the TV
series/movie started to the title (e.g. "13-reasons-why-2017")
or the determiner in a different place (e.g. "incredible-hulk-the)
If that doesn't work, there might be no transscripts for what
you're searching for on springfieldspringfield.co.uk.\n""")
