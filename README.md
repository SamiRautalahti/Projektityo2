# Sääsovellus Pythonilla

Tämä sääsovellus on Pythonilla toteutettu sovellus, joka käyttää FMI Open Data -rajapintaa säätietojen hakemiseen. Sovellus tallentaa säätiedot SQL-tietokantaan ja tarjoaa yksinkertaisen web-käyttöliittymän tietojen näyttämiseen.
Toiminta

• Säädatan haku: Sovellus käyttää FMI Open Data -rajapintaa hakeakseen ajantasaista säätietoa eri havaintoasemilta.

• Tietokanta: Haetut säätiedot tallennetaan SQL-tietokantaan, jotta niitä voidaan käsitellä ja näyttää joustavasti.

• Web-käyttöliittymä: Sovellus tarjoaa yksinkertaisen web-käyttöliittymän, jossa käyttäjä voi nähdä tallennetut säätiedot taulukkomuodossa.

Asennus

• Kloonaa repository.

• Asenna tarvittavat kirjastot: pip install -r requirements.txt.

• Aseta SQL-tietokantaan liittyvät tiedot config.py-tiedostoon.

• Suorita sovellus: python main_app.py.

• Avaa selain ja siirry osoitteeseen http://localhost:5000 nähdäksesi säätiedot.

Lisätiedot

• Lisätietoja sovelluksen toiminnasta, kontribuoinnista ja lisenssistä löydät README.md-tiedostosta.

Huomautus

• Sovellus on tarkoitettu opetuskäyttöön, ja sen tulee noudattaa FMI Open Data -palvelun käyttöehtoja.
