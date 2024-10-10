import requests
from bs4 import BeautifulSoup
import re
#Ovan import av de relevanta externa biblioteken

#Classer = Classes (det bär mig emot att skriva på Svenska/Svengelska - under kodning kör jag till 90% Engelska)
# Class för att extrahera titeln
class TitleExtractor:
    def __init__(self, soup):
        self.soup = soup

    def extract_title(self):
        return self.soup.title.text if self.soup.title else 'No title found'

# Class för att extrahera sub-titlar
class SubTitleExtractor:
    def __init__(self, soup):
        self.soup = soup

    def extract_subtitles(self):
        # Finn alla <h1>, <h2> och <h3> tags (du kan välja fler/färre)
        subtitles = []
        for tag in self.soup.find_all(['h1', 'h2', 'h3']):
            subtitles.append(tag.text)
        return subtitles

# Class för att extrahera länkar
class LinkExtractor:
    def __init__(self, soup):
        self.soup = soup

    def extract_links(self):
        links = []
        for link in self.soup.find_all('a'):
            href = link.get('href')
            if href:
                links.append(href)
        return links

# Class för att extrahera telefonnummer
class PhoneNumberExtractor:
    def __init__(self, soup):
        self.soup = soup

    def extract_phone_numbers(self):
        # Olika regex-mönster för att identifiera telefonnummer i sträng (här fick jag labba/testa ganska mycket)
        phone_pattern = re.compile(
            r'(tel:\+?0*46[-.\s]?\(?0?\)?[-.\s]?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4})|'  # tel:0004643110666 format
            r'(\+[-.\s]?\d{1,3}\s?\(?0?\)?[-.\s]?\d{1,3}[-.\s]?\d{1,3}[-.\s]?\d{2,4}[-.\s]?\d{2,4})|'  # + 46 (0) xxx xxx xx
            r'(\+46\d{9})|'  # +46706706666 format
            r'(0\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4})|'  # 070-xxx-xxxx, 070 xxxx xx xx etc.
            r'(00046\d{9})|'  # 00046706706666 format 070-nummer (tot 9 utan 0 - riktnummer 3 siffror)
            r'(00046\d{8})|'  # 0004686706666 format 08-nummer (tot 8 utan 0 - riktnummer 2 siffror)
            r'(00046\d{10})'  # 000464316706666 format 0431 (tot 10 utan 0 - riktnummer 4 siffror)
        )

        # Extrahera telefonnummer från href som <a href="tel:...">
        phone_numbers_href = []
        for tag in self.soup.find_all('a', href=True):
            if 'tel:' in tag['href']:
                phone_numbers_href.append(tag['href'])

        # Hitta telefonnummer i övriga texten
        text_content = self.soup.get_text()
        phone_numbers_text = phone_pattern.findall(text_content)
        phone_numbers_text = [''.join(number) for number in phone_numbers_text if ''.join(number)]

        return phone_numbers_href, phone_numbers_text

# Scraping Huvudprocess
class WebScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def fetch_html(self):
        headers = { #Fick fel 403, tog reda på "user-agent"-fix för siter där servern blockar icke-browsrar - detta gör att python lurar servern att det är en browser.
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        #Skickar GET request och parsear HTML-innehåll.
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'html.parser')
            print("Lyckad HTML-skrapning.")

            raw_HTML_filename = f"scrapeHTML_{domain_name}.txt"
            #Sparar rå HTMLkod till en fil. (för kvalitetskontroll)
            with open(raw_HTML_filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Rå HTML-kod sparad till filen {raw_HTML_filename}")

        else:
            print(f"Misslyckad skrapning, status code: {response.status_code}")

    def save_raw_text(self, filename):
        #Sparar komplett websideinnehåll till en fil. (för kvalitetskontroll)
        with open(filename, 'w', encoding='utf-8') as file:
            text_content = self.soup.get_text()
            file.write(text_content)
        print(f"Komplett hemsidetext sparad till filen {filename}")

    def save_to_file(self, filename, title, subtitles, links, phone_numbers_href, phone_numbers_text):
        #Sparar diverse info koncentrerat till en fil.
        with open(filename, 'w', encoding='utf-8') as file:
            # Skriv huvudtitel
            file.write(f"Sidans huvudtitel: {title}\n\n")
            
            # Skriv sub-titlar
            file.write(f"********** SUB TITLAR ************\n")
            file.write("Sub-titlar på sidan:\n")
            for subtitle in subtitles:
                file.write(f"{subtitle}\n")
                file.write(f"----\n")

            # Skriv länkar
            file.write(f"\n********* LÄNKAR *************\n")
            file.write("Länkar på sidan:\n")
            for link in links:
                file.write(f"{link}\n")
            
            # Telefonnummer från href 
            file.write(f"\n********* TELEFONNUMMER *************\n")
            file.write("Telefonnummer från (från href) på sidan:\n")
            for number in phone_numbers_href:
                file.write(f"{number}\n")
            
            # Telefonnummer från texten i övrigt
            file.write("\nTelefonnummer från texten i övrigt på sidan:\n")
            for number in phone_numbers_text:
                file.write(f"{number}\n")
        
        print(f"Koncentrerad extraherad information sparat till filen {filename}")
    
    def ask_user_for_output(self, title, subtitles, links, phone_numbers_href, phone_numbers_text):
        #Fråga användaren vad som önskas skrivas ut från extraherad data i loop tills valet "exit".
        while True:
            print("\nVad önskas skrivas ut från extraherad data?")
            print("1. Titel")
            print("2. Sub-titlar")
            print("3. Länkar")
            print("4. Telefonnummer")
            print("5. Exit")
            choice = input("Välj ett nummer ovan: ")

            if choice == "1":
                print(f"\nTitel: {title}")
            elif choice == "2":
                print("\nSub-titlar på sidan:")
                for subtitle in subtitles:
                    print(subtitle)
            elif choice == "3":
                print("\nLänkar på sidan:")
                for link in links:
                    print(link)
            elif choice == "4":
                print("\nTelefonnummer (från href):")
                for number in phone_numbers_href:
                    print(number)
                print("\nTelefonnummer (från övrig text):")
                for number in phone_numbers_text:
                    print(number)
            elif choice == "5":
                print("\nAvbryter - tack för visat intresse...\n")
                break
            else:
                print("Felaktigt val, vänligen försök igen.")

# Start webbskrapare
url = input("Vänligen ange URL för en websida: ") #Ber användaren ange. #Idé: Läs in textfil med flera url...
domain_name = url.split('//')[-1].split('/')[0] #Tar bort allt före // inkl dessa, samt allt efter huvuddomänen dvs directories (ändrar ej skrapplats/dir)
scraper = WebScraper(url)
scraper.fetch_html()

if scraper.soup:
    # Extrahera titeln
    title_extractor = TitleExtractor(scraper.soup)
    title = title_extractor.extract_title()

    # Extrahera sub-titlar
    subtitle_extractor = SubTitleExtractor(scraper.soup)
    subtitles = subtitle_extractor.extract_subtitles()
    
    # Extrahera länkar
    link_extractor = LinkExtractor(scraper.soup)
    links = link_extractor.extract_links()

    # Extrahera telefonnummer
    phone_extractor = PhoneNumberExtractor(scraper.soup)
    phone_numbers_href, phone_numbers_text = phone_extractor.extract_phone_numbers()

    # Spara koncentrerad extraherad information till en fil - HUVUDFILEN
    filename = f"scrapeRESULT_{domain_name}.txt"
    scraper.save_to_file(filename, title, subtitles, links, phone_numbers_href, phone_numbers_text)
    
    # Sparar komplett websideinnehåll till en fil. (för kvalitetskontroll)
    raw_text_filename = f"scrapeRAW_{domain_name}.txt"
    scraper.save_raw_text(raw_text_filename)

    # Skriva ut resultat för användaren i en loop till valet exit
    scraper.ask_user_for_output(title, subtitles, links, phone_numbers_href, phone_numbers_text)