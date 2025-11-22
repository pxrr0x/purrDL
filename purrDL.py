"""
Author: Prince Addai Desmond | pxrr0x
Email: pxrr0x.dev@gmail.com
Github: github.com/pxrr0x

Date: 2025-11-22
Description: turboG or turboGranny is a CLI Python utility that scrapes YTS, retrieves torrent files, and automatically downloads them. 
             It is designed to be used on Linux and Android(Termux), offering a simple 
             and fast way to download movies directly from the terminal. ;)
"""

from bs4 import BeautifulSoup
import os
import platform
import subprocess
import sys
import time
import requests
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)



TMP_DIR = "./.tmp/files"

# Colors class
class COLORS:
    bold = "\033[1m"
    bold_white = "\033[1;97m"
    gray = "\033[1;37m"
    red = "\033[1;91m"
    blue = "\033[1;94m"
    yellow = "\033[1;93m"
    reset = "\033[0m"


def main():
    try:
        art()
        args = sys.argv[1:]
        query = '+'.join(args)

        movie, title = scrape_yts(query)
        if movie == "none":
            print("Couldn't load movie's data")
            sys.exit(2)

        name, url = scrape_movie(movie)
        if url == "none":
            print("Couldn't load movie's sources")
            sys.exit(3)
            
        clean(TMP_DIR)
        os.makedirs(TMP_DIR, exist_ok=True)
        os.chmod(TMP_DIR, 0o755)

        try:
            name = name.split("/")
            name = "-".join(name)
        except:
            pass
        filename = f"{name}.torrent"
        path = os.path.join(TMP_DIR, filename)

        try:
            subprocess.run(["curl","-sS", "-o", path, url])
            time.sleep(1)
            download_path = get_download_path()
            time.sleep(1)
            
            if (detect_env() == "linux"):
                unhide(download_path, title)
                download_torrent_linux(path)
                hide(download_path, title)
            elif (detect_env() == "termux"):
                unhide(download_path, title)
                download_torrent_termux(download_path, path, title)
                hide(download_path, title)
            
            hide(download_path, title)
            clean(TMP_DIR)
            exit()
        except Exception as e:
            clean(TMP_DIR)
            hide(download_path, title)
            exit()
    except requests.exceptions.ConnectionError:
        clean(TMP_DIR)
        hide(download_path, title)
        print(f"{COLORS.red}Connect to the internet 🥲{COLORS.reset}")
        sys.exit(1)
    except KeyboardInterrupt:
        hide(download_path, title)   
        clean(TMP_DIR)
        print("\nBai Baii ♥")
        sys.exit(0)
    except Exception:
        clean(TMP_DIR)
        hide(download_path, title)
        exit(1)


# Deletes donwloaded torrents
def clean(TMP_DIR):
    if os.path.exists(TMP_DIR):
        files = os.listdir(TMP_DIR)
        if files:
            for file in files:
                file_path = os.path.join(TMP_DIR, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    pass


# Scrapes the homepage
def scrape_yts(query):
    try:
        url = f"https://yts.lt/browse-movies/{query}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        titles = []
        links = []
        # Prints out each movie(title to titles array and link to links array) 
        for movie in soup.find_all('div', class_ = 'browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4') :
            title = movie.find('div', class_ = 'browse-movie-bottom').text.splitlines()
            link = movie.find('a', class_ = 'browse-movie-link') ['href']
            
            titles.append(f"{title[1]} - {title[2]}")
            links.append(link)

        # Prints out each title in titles and link in links
        count = 0
        print(f"{COLORS.red}[{count:02}]  Exit{COLORS.reset}")
        print()
        count += 1 
        for title in titles:
            print(f"[{count:02}]  {COLORS.bold}{title}{COLORS.reset}")
            print()
            count += 1 
        print("\n")

        while True:
            number = int(input(f"{COLORS.blue}Select a movie[01 - {count-1:02}]: {COLORS.reset}"))
            if not(number > count) and not(number < 0):
                break 

        if number == 0:
            print("\nBai Baii ♥")
            sys.exit(0)

        for i in range(len(links)):
            if number == i+1:
                return links[i], titles[i]
        return "none"
    except KeyboardInterrupt:
        pass


# Scrapes the movie page
def scrape_movie(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        data = soup.find('p', class_ = 'hidden-md hidden-lg')

        titles = []
        torrents = []
        a_tags = data.find_all('a')
        for a in a_tags:
            title = str(a['title'])
            torrent = str(a['href'])
            
            if not("subtitles" in title.lower() or "subtitles" in torrent.lower()):
                titles.append(title)
                torrents.append(torrent)
            
        if len(titles) == len(torrents):
            count = 0
        else:
            print("Sumn's wrong fs")
        
        print(f"\n{COLORS.yellow}Available Sources:{COLORS.reset}\n")
        print(f"{COLORS.red}[{count:02}]  Go back{COLORS.reset}\n")
        count += 1
        for title in titles:
            if "Torrent" in title:
                title = title.replace("Torrent", "")
            print(f"[{count:02}]  {COLORS.bold}{title}{COLORS.reset}")
            print()
            count += 1
        print("\n")
        
        number = input(f"{COLORS.blue}Select a resolution to download[01 - {count-1:02}]: {COLORS.reset}")
        while True:
            while not number.isnumeric():
                number = input(f"Select a resolution to download[1 - {count-1}]: ")

            number = int(number)
            if not(number > count) and not(number < 0):
                break 

        if number == 0:
            print("\n🔙 {}BACK{}\n".format(COLORS.red,COLORS.reset))
            main()

        for i in range(len(torrents)):
            if number == i+1:
                return titles[i] ,torrents[i]
        return "none" , "none"
    except KeyboardInterrupt:
        pass

# Gets download path
def get_download_path():
    try:
        linux = os.path.expanduser("~/Downloads")
        termux = os.path.expanduser("~/storage/downloads")

        if os.getenv("TERMUX_VERSION") and os.path.exists(os.path.expanduser("~/storage")):
            return termux
        elif os.path.exists(os.path.expanduser(("~/Downloads"))):
            return linux
    except KeyboardInterrupt:
        pass

# Just read the code. Its really conspicuous
def detect_env():
    try: 
        if os.path.exists("/data/data/com.termux/files/usr/bin/pkg"):
            return "termux"
        elif platform.system().lower() == "linux":
            return "linux"
        else:
            return "unknown"
    except KeyboardInterrupt:
        pass


# Hides the log files in download path
def hide(path, title):
    try:
        title = title.split('-')
        ext = "aria2"
        if os.path.exists(path):
            files = os.listdir(path)
            for file in files:
                if title[0] in file and ext in file and not str(file).startswith('.'):
                    file_path = os.path.join(path,file)
                    hidden_path = os.path.join(path, f".{file}")
                    try:
                        os.rename(file_path, hidden_path)
                    except:
                        pass
    except KeyboardInterrupt:
        pass

# Opposite of hide
def unhide(path, title):
    try:
        title = title.split('-')
        ext = "aria2"
        if os.path.exists(path):
            files = os.listdir(path)
            for file in files:
                if title[0] in file and ext in file and str(file).startswith('.'):
                    hidden_path = os.path.join(path,file)
                    file_path = os.path.join(path, file[1:])
                    try:
                        os.rename(hidden_path, file_path)
                    except:
                        pass          
    except KeyboardInterrupt:
        pass

# TODO
def man():
    manual = """
    TurboGranny Movie Downloader

    Usage:
        python3 turboG.py 
"""


def download_torrent_linux(path):
    import libtorrent as lt
    ses = lt.session()
    ses.listen_on(6881, 6891)  # No warning shown now
    try:
        if not os.path.exists(path):
            print(f"{COLORS.red}Error: .torrent not found{COLORS.reset}")
            sys.exit() # TODO: give appropriate exit code

        save_path = get_download_path()

        ses = lt.session()
        ses.listen_on(6881, 6891)

        params = {''
            'save_path': save_path,
            'ti': lt.torrent_info(path),
        }

        handle = ses.add_torrent(params)

        print(f"{COLORS.blue}Starting download:{COLORS.reset} {COLORS.bold}{handle.name()}{COLORS.reset}")
        print(f"{COLORS.blue}Saving to:{COLORS.reset} {COLORS.bold}{save_path}{COLORS.reset}")
        print(f"{COLORS.red}Press Ctrl+C to pause/stop downloading{COLORS.reset}\n")

        try:
            while True:
                d = handle.status()

                print("\rDownloading: %.f%% complete (%.1f/%.1f MB) down🠳: %.1f kB/s up🠱: %.1f kB/s peers: %d" % 
                    ( d.progress * 100, d.total_done / (1024 * 1024), d.total_wanted / (1024 * 1024), d.download_rate / 1024, d.upload_rate / 1024,
                    d.num_peers), end="  ")
                
                if d.is_seeding:
                    print(f"\n{COLORS.bold}Download complete!{COLORS.reset}")
                    break

                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{COLORS.bold}Pausing download...{COLORS.reset}")
            handle.pause()
            print(f"{COLORS.bold}Download Paused. You can resume later.{COLORS.reset}")  
        except Exception as e:
            print(f"\n{COLORS.red}An error occurred: {e}{COLORS.reset}")
            return False
        return True
    except KeyboardInterrupt:
        pass


def download_torrent_termux(download_path, path, title):
    try:
        subprocess.run(["aria2c", "-d", download_path, path, "--allow-overwrite=true"], check=True)
        print(f"\n{COLORS.bold}Download complete!{COLORS.reset}")
        return True
    
    except KeyboardInterrupt:
        print(f"\n{COLORS.bold}Pausing download...{COLORS.reset}")
        print(f"{COLORS.bold}Download Paused. You can resume later.{COLORS.reset}") 
    except subprocess.CalledProcessError as e:
        clean(TMP_DIR)
        hide(download_path, title)
        exit()
    except Exception as e:
        print(f"\n{COLORS.red}An error occurred: {e}{COLORS.reset}")
        return False
    return True

# Skip :)
def art():
    try:
        desc = "Fast and Simple Movie Downloader"
        version = "25.11.22"
        author = "https://github.com/pxrr0x/"
        art = r'''
     /\_/\      {3}purrDL{4} v{0}
    ( o.o )     {1}
     > ^ <      ~ {2} ~
        '''.format(version, desc, author, COLORS.bold, COLORS.reset)

        subprocess.run(f"echo \"{art}\" | lolcat", shell=True)
    except FileNotFoundError:
        print(f"Missing dependencies, please install them.\nExecute: {COLORS.bold}python3 install.py{COLORS.reset}")  
    except KeyboardInterrupt:
        pass
    except Exception:
        pass     

if __name__ == "__main__":
    main()