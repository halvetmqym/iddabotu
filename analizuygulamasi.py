import subprocess
import sys
import importlib
import requests
from bs4 import BeautifulSoup as bs
from googletrans import Translator

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

def install_and_import(package):
    try:
        importlib.import_module(package)
        print(f"'{package}' kütüphanesi zaten yüklü.")
    except ImportError:
        print(f"'{package}' kütüphanesi yüklü değil, yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"'{package}' kütüphanesi başarıyla yüklendi.")

# Gerekli kütüphaneler
packages = ['requests', 'bs4', 'googletrans==4.0.0-rc1', 'kivy']

for package in packages:
    install_and_import(package)

class MatchAnalysisApp(App):
    def build(self):
        self.title = "Maç Analiz ve Tahmin"
        
        layout = BoxLayout(orientation='vertical')
        
        self.header = Label(text="Maç Analiz ve Tahmin", font_size='20sp', size_hint=(1, 0.1))
        layout.add_widget(self.header)
        
        self.matches_label = Label(text=self.get_matches(), font_size='10sp', size_hint=(1, None))
        self.matches_label.bind(texture_size=self.matches_label.setter('size'))
        
        matches_scroll = ScrollView(size_hint=(1, 0.3), do_scroll_x=False, do_scroll_y=True)
        matches_scroll.add_widget(self.matches_label)
        layout.add_widget(matches_scroll)
        
        self.result_label = Label(text="", font_size='10sp', size_hint=(None, None), width=800)
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        
        results_scroll = ScrollView(size_hint=(1, 0.4), do_scroll_x=True, do_scroll_y=True)
        results_scroll.add_widget(self.result_label)
        layout.add_widget(results_scroll)
        
        self.team_input = TextInput(hint_text='Takım isimlerini yazınız', multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.team_input)
        
        self.submit_button = Button(text='Analiz Yap', on_press=self.on_submit, size_hint=(1, 0.1))
        layout.add_widget(self.submit_button)
        
        return layout

    def get_matches(self):
        url = 'https://www.over25tips.com/free-football-betting-tips/tomorrow/'
        resp = requests.get(url)
        matches_text = "Maçlar:\n"
        
        if resp.status_code == 200:
            html = bs(resp.content, 'html.parser')
            matches = html.find_all('h3', class_='h2prediction')
            for i, match in enumerate(matches, 1):
                matches_text += f"{i}. {match.text.strip()}\n"
        return matches_text

    def on_submit(self, instance):
        team_name = self.team_input.text.strip().lower()
        self.result_label.text = "Yükleniyor...\n"
        
        if team_name == 'quit':
            self.stop()
        else:
            self.result_label.text += f"{team_name.capitalize()} için analiz yapılıyor...\n"
            analysis_text = self.fetch_analysis(team_name)
            self.result_label.text += analysis_text
            self.result_label.text += "\n"

    def fetch_analysis(self, team_name):
        url = 'https://www.over25tips.com/free-football-betting-tips/tomorrow/'
        url2 = 'https://www.over25tips.com'
        
        resp = requests.get(url)
        
        if resp.status_code == 200:
            html = bs(resp.content, 'html.parser')
            match_links = html.find_all('a', class_='stats-btn')
            
            for link in match_links:
                if team_name in link.get('href'):
                    url3 = url2 + link.get('href')
                    return self.get_analysis(url3)
        return "Maç bulunamadı."

    def get_analysis(self, url3):
        response2 = requests.get(url3)
        analysis_page = bs(response2.content, 'html.parser')
        
        metin1 = analysis_page.find('h2', class_='h2-super blo')
        metin2 = analysis_page.find_all('p')
        
        translator = Translator()
        result = ""
        
        if metin1:
            result += self.translate_and_break_lines(metin1.text.strip().upper()) + "\n\n"
        
        for metin in metin2:
            result += self.translate_and_break_lines(metin.text.strip()) + "\n\n"
        
        metin3 = analysis_page.find('div', class_='col-xs-12 text-xs-center center-align')
        
        if metin3:
            result += self.translate_and_break_lines(metin3.text.strip().upper()) + "\n\n"
        
        return result
    
    def translate_and_break_lines(self, text, max_chars=80):
        translator = Translator()
        translated_text = translator.translate(text, src='en', dest='tr').text
        
        lines = []
        current_line = ""
        
        for word in translated_text.split():
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return "\n".join(lines)

if __name__ == '__main__':
    MatchAnalysisApp().run()
