# MAP · Marseille AddictoPsy

Application web installable (sur iPhone et Android, sans store) pour orienter les patients en consultation :
addictologie (cures, post-cures, hôpitaux de jour, CSAPA, hébergement, réduction des risques, médecins libéraux),
CMP adultes de secteur de Marseille (avec le rattachement par date de naissance pour les personnes sans domicile),
équipes mobiles et urgences psychiatriques.

Ouvrir : https://mapannuaire.github.io/map/

Les informations (numéros, adresses, formulaires) évoluent : vérifier avant tout envoi.


## Licence

Le code de MAP · Marseille AddictoPsy (application, page de statistiques, scripts du dossier `outils/` et actions GitHub) est publié sous **licence publique de l'Union européenne, EUPL 1.2** : voir le fichier [LICENSE](LICENSE). Vous pouvez le réutiliser, le modifier et le redistribuer, par exemple pour créer l'annuaire d'un autre territoire. Si vous diffusez une version modifiée, elle doit rester sous EUPL (ou une licence compatible) et son code doit rester accessible.

© 2026 Julien Aron et les contributeurs de MAP · Marseille AddictoPsy.

### Ce que la licence ne couvre pas

- **Les données des fiches** (lieux, horaires, contacts, textes) : elles ne sont pas sous licence libre pour l'instant. Une partie provient de cartographies réalisées avec GoGoCarto et d'autres sources citées dans les fiches.
- **Les photos et plaquettes** du dossier `medias/` : elles restent la propriété de leurs auteurs, qui ont accepté leur publication dans MAP.
- **Les composants tiers**, qui gardent leur propre licence :
  - jsPDF et html2canvas (dossier `vendor/`) : licence MIT ;
  - qrcode-generator de Kazuhiko Arase, intégré à l'application : licence MIT ;
  - Leaflet, intégré à l'application : licence BSD 2 clauses ;
  - polices Newsreader et IBM Plex : SIL Open Font License 1.1 ;
  - fonds de carte © contributeurs d'OpenStreetMap, données sous licence ODbL.
- Les dossiers `bpm-marseille/` et `geocode/` relèvent d'autres projets.
