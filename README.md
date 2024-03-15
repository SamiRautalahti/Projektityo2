# Sääsovellus Pythonilla

Tämä sääsovellus on Pythonilla toteutettu sovellus, joka käyttää FMI Open Data -rajapintaa säätietojen hakemiseen. Sovellus tallentaa säätiedot SQL-tietokantaan ja tarjoaa yksinkertaisen web-käyttöliittymän tietojen näyttämiseen.
Toiminta

• Säädatan haku: Sovellus käyttää FMI Open Data -rajapintaa hakeakseen ajantasaista säätietoa eri havaintoasemilta.

• Tietokanta: Haetut säätiedot tallennetaan SQL-tietokantaan, jotta niitä voidaan käsitellä ja näyttää joustavasti.

• Web-käyttöliittymä: Sovellus tarjoaa yksinkertaisen web-käyttöliittymän, jossa käyttäjä voi nähdä tallennetut säätiedot taulukkomuodossa.

Asennus

• Kloonaa repository.

• Asenna tarvittavat kirjastot: pip install -r requirements.txt.

• Aseta SQL-tietokantaan liittyvät tiedot main.py:n riveille 21-26

• Suorita sovellus: python main_app.py.

• Avaa SQL-tietokanta Power BI:ssä raporttia/visualisointia varten.
