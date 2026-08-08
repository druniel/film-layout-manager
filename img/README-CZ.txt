FILMANA LAYOUT – IKONA PRO WINDOWS
==================================

Doporučený hlavní soubor:
  ico/filmana-layout-transparent.ico

Jde o vícevelikostní Windows ikonu s průhledným pozadím. Obsahuje vrstvy
16, 20, 24, 32, 40, 48, 64, 96, 128 a 256 px. Bílý znak a zlaté prvky mají
jemnou tmavou konturu, aby zůstaly čitelné ve světlém i tmavém motivu Windows.

Bezpečnější alternativa pro nejmenší zobrazení:
  ico/filmana-layout-dark-tile.ico

Černá dlaždice drží značku pohromadě a bývá lépe rozpoznatelná při 16–24 px.
Vnější rohy jsou průhledné.

PNG soubory:
  filmana-layout-transparent.png   průhledný master 1024 × 1024 px
  filmana-layout-dark-tile.png     černá dlaždice 1024 × 1024 px
  png/transparent/                 jednotlivé průhledné velikosti
  png/dark-tile/                   jednotlivé velikosti s černou dlaždicí

Běžné použití:
  • WinForms / WPF / .NET: nastavte soubor .ico jako Application Icon.
  • Electron: použijte .ico pro Windows build a 512px PNG pro náhledy.
  • PyInstaller: parametr --icon=filmana-layout-transparent.ico
  • Zástupce ve Windows: Vlastnosti → Změnit ikonu → vyberte .ico.

Poznámka:
Windows někdy uchovává starou ikonu v mezipaměti. Po výměně může být nutné
znovu vytvořit zástupce, odhlásit se, případně restartovat Průzkumníka Windows.

