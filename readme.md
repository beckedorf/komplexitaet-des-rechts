Komplexität des Rechts
======================

Dieser Online-Appendix ergänzt die Publikation:

> Janis Beckedorf, Komplexität des Rechts: Eine quantitative Untersuchung der Struktur des Rechts, Mohr Siebeck, 2025 Tübingen (im Erscheinen), https://doi.org/10.1628/978-3-16-164476-4


Ergänzende Materialien
----------------------

Der Online-Appendix enthält alle datenbasierten Abbildungen der Publikation in Farbe sowie weitere ergänzende Materialien und insbesondere:

- Verzeichnis der Gesetzesabkürzungen in Kapitel 4: [tables/de_gesetze_abks.md](tables/de_gesetze_abks.md)
- Abbildung 4.32 (Gesetze bzw. Bücher für das Jahr 2019 mit mehr als 5000 Tokens): [data_figures/meso_quotient_graph_de_buch_2019.pdf](data_figures/meso_quotient_graph_de_buch_2019.pdf)
- Abbildung 4.33 (Konsens-Gruppierung der Gesetze bzw. Bücher für das Jahr 2019 mittels des Louvain-Algorithmus):  [data_figures/meso_quotient_graph_de_community_louvain_mixed_2019.pdf](data_figures/meso_quotient_graph_de_community_louvain_mixed_2019.pdf)
- Kapitel 4, Fußnote 116 (Feinere Gruppierung mittels des Louvain-Algorithmus): [tables/meso_de_2019_louvain_mixed_detailed.txt](tables/meso_de_2019_louvain_mixed_detailed.txt)
- Abbildung 4.34 (Konsens-Gruppierung der Gesetze bzw. Bücher durch den Infomap-Algorithmus auf Basis der Querverweise und Kookkurrenzen): [data_figures/sankey_de_0-0_1-0_-1_o-2-0_t-paragraph_a-infomap_n100_m1-0_s0_c1000_labels.pdf](data_figures/sankey_de_0-0_1-0_-1_o-2-0_t-paragraph_a-infomap_n100_m1-0_s0_c1000_labels.pdf). Die Inhalte der Gruppen werden in [tables/all_0-0_1-0_-1_o-2-0_t-paragraph_a-infomap_n100_m1-0_s0_c1000.htm](tables/all_0-0_1-0_-1_o-2-0_t-paragraph_a-infomap_n100_m1-0_s0_c1000.htm) aufgelistet. (Die .htm Datei kann heruntergeladen und im Webbrowser geöffnet werden.)

Weitere Grafiken finden Sie im Ordner `data_figures`.


Replikation der Analyse
-----------------------

Die publikationsspezifischen Analysen wurde in Jupyter Notebooks durchgeführt, die im Ordner `notebooks` enthalten sind.

Um diese Notebooks erfolgreich auszuführen, müssen folgende Voraussetzungen erfüllt sein:
1. Neben diesem Ordner `komplexitaet-des-rechts` muss der zugehörige Datensatz im Ordner `legal-networks-data` gespeichert werden. Der Datensatz ist unter https://doi.org/10.1628/978-3-16-164476-4-appendix verfügbar. Das heruntergeladene ZIP-Archiv muss entpackt werden. In den entpackten Verzeichnissen `de`, `de_decisions` und `us` befinden sich weitere ZIP-Archive, die ebenfalls entpackt werden müssen.
2. Ebenfalls neben diesem Ordner `komplexitaet-des-rechts` ist im Ordner `legal-data-clustering` der Programmcode zur Gruppierung der Graphen zu speichern. Wenn der Appendix von https://doi.org/10.1628/978-3-16-164476-4-appendix heruntergeladen wurde ist dies bereits gegeben.
3. Die in der Datei `requirements.txt` angegebenen Python-Pakete müssen installiert sein. 
    - Alternativ kann für eine vereinfachte Einrichtung der Entwicklungsumgebung [Docker](https://docker.com) als Containervirtualisierung verwendet werden. Mit dem Befehl `bash startjupyter.sh` wird ein Docker-Image mit allen benötigten Paketen erstellt und Jupyter Notebook gestartet.
