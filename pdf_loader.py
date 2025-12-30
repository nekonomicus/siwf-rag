"""
PDF Content Loader
Pre-extracted PDF content for the RAG system
"""
import requests
import os

# Pre-loaded content for the orthopedics PDF
# This is the content from the SIWF orthopedics training program
ORTHOPEDICS_PDF_CONTENT = """
SIWF FMH ISFM

Fachärztin oder Facharzt für Orthopädische Chirurgie und Traumatologie des Bewegungsapparates

Weiterbildungsprogramm vom 1. Juli 2022

Akkreditiert durch das Eidgenössische Departement des Innern: 31. August 2018

1. Allgemeines

1.1 Umschreibung des Fachgebietes

Die Orthopädische Chirurgie und Traumatologie des Bewegungsapparates befasst sich mit dem gesamten Spektrum der Entwicklungsstörungen, Erkrankungen, den Verletzungen und den Verletzungsfolgen des Bewegungsapparates in jedem Lebensalter.

1.2 Ziel der Weiterbildung

Ziel der Weiterbildung zur Fachärztin oder zum Facharzt für Orthopädische Chirurgie und Traumatologie des Bewegungsapparates ist das Erwerben von fundierten Kenntnissen über Erkrankungen und Verletzungen des Bewegungsapparates und deren Folgen. Die Fachärztin oder der Facharzt für Orthopädische Chirurgie und Traumatologie ist fähig, diese Zustände in eigener Kompetenz, insbesondere auch unter Miteinbezug des sozioökonomischen Umfeldes, operativ und nicht-operativ zu behandeln.

Patientinnen und Patienten, Hausärztinnen und Hausärzte, Versichernde, Gesetzgebende und die Fachgesellschaft für Orthopädie und Traumatologie erwarten von einer Fachärztin oder einem Facharzt Kompetenz sowie soziale und ethische Integrität in der Diagnostik, Beurteilung, Behandlung und Nachsorge von angeborenen und erworbenen Störungen oder Läsionen des Bewegungsapparates. Die Therapie von seltenen oder komplexen Erkrankungen bzw. Verletzungen am Bewegungsapparat gehört in ein entsprechend ausgewiesenes und ausgerüstetes Zentrumsspital. Jede Fachärztin und jeder Facharzt für Orthopädie und Traumatologie muss jedoch auch seltene Krankheitsbilder erkennen, um eine zweckmäßige Triage und Weiterweisung vornehmen zu können.

2. Dauer, Gliederung der Weiterbildung und weitere Bestimmungen

2.1 Dauer und Gliederung der Weiterbildung

2.1.1 Die Weiterbildung dauert 6 Jahre. Sie gliedert sich wie folgt in:
- 0-1 Jahr Basisweiterbildung (nicht fachspezifisch; vgl. Ziffer 2.1.2)
- 5-6 Jahre fachspezifische Weiterbildung (vgl. Ziffer 2.1.3)

2.1.2 Basisweiterbildung (nicht fachspezifisch)

Die Basisweiterbildung kann in folgenden Fachgebieten absolviert werden:
- Allgemeine Innere Medizin
- Anästhesiologie
- Chirurgie
- Gefässchirurgie
- Handchirurgie
- Herz- und thorakale Gefässchirurgie
- Intensivmedizin
- Kinderchirurgie
- Mund-, Kiefer- und Gesichtschirurgie
- Neurochirurgie
- Neurologie
- Oto-Rhino-Laryngologie
- Plastische, rekonstruktive und ästhetische Chirurgie
- Rheumatologie
- Thoraxchirurgie
- Urologie

2.1.3 Fachspezifische Weiterbildung

Orthopädische Weiterbildung:
Mindestens 3 Jahre der fachspezifischen Weiterbildung sind an Weiterbildungsstätten für orthopädische Chirurgie zu absolvieren, davon mindestens 2 Jahre an Weiterbildungsstätten der Kategorie A.

Traumatologische Weiterbildung:
Mindestens 3 Jahre der fachspezifischen Weiterbildung sind an Weiterbildungsstätten für orthopädische Chirurgie durchzuführen, die auch für die Weiterbildung in Traumatologie des Bewegungsapparates (Kategorie 1 oder 2) anerkannt sind.

Alternativ können höchstens 2 dieser 3 Jahre an Weiterbildungsstätten absolviert werden, die für den Schwerpunkt Allgemeinchirurgie und Traumatologie anerkannt sind (ACT1 bzw. ACT2).

Es muss mindestens 1 Jahr Traumatologie der Kategorie 1 an Weiterbildungsstätten für orthopädische Chirurgie absolviert werden.

2.1.4 Forschung bzw. MD-PhD-Programm

An die 6-jährige Weiterbildung kann maximal 1 Jahr Forschung oder eine abgeschlossene MD-PhD-Ausbildung angerechnet werden. Wenn es sich um Forschung im Zusammenhang mit dem Bewegungsapparat handelt, können davon maximal 6 Monate als fachspezifische Weiterbildung angerechnet werden. Diese Periode gilt nicht als Kategorie A. Es empfiehlt sich, vorgängig die Titelkommission anzufragen.

2.1.5 Praxisassistenz

Eine Weiterbildung als Praxisassistentin oder Praxisassistent wird weder für die fachspezifische noch für die nicht fachspezifische Weiterbildung anerkannt.

2.2 Weitere Bestimmungen

2.2.1 Erfüllung der Lernziele/Logbuch

Erfüllung der Lernziele gemäss Ziffer 3. Jede Kandidatin und jeder Kandidat führt regelmässig ein Logbuch, welches die Lernziele der Weiterbildung enthält und in welchem alle geforderten Lernschritte dokumentiert werden. Die Kandidatin oder der Kandidat legt das Logbuch seinem Titelgesuch bei.

2.2.2 Technische Orthopädie

- Ausweis über den Besuch des 1½-tägigen Einführungskurses der Schweizerischen Arbeitsgemeinschaft für Prothesen und Orthesen APO (http://www.swissorthopaedics.ch/ → Weiterbildung oder www.a-p-o.ch).
- Nachweis von 5 Arbeitstagen in von swiss orthopaedics anerkannten orthopädischen Werkstätten (vgl. www.orthorehasuisse.ch)

2.2.3 Kurse

Absolvieren der obligatorischen Kurse gemäss Ziffer 4.

2.2.4 Facharztprüfung

Bestandene Facharztprüfung. Für die Anmeldung zur Schlussprüfung muss die Anatomie-Prüfung bestanden sein. Zur Zulassung zur Facharztprüfung muss mindestens 1 Jahr an einer Weiterbildungsstätte der Kategorie A absolviert sein.

OPERATIONSKATALOG

Mindestzahl von 450 Operationen als Operateurin oder Operateur. Davon sind mindestens 200 in erster Assistenz zu absolvieren.

Prothetik - minimal 30, maximal anrechenbar 90:
- Hüfte: Totalprothese, Hemiprothese, Prothesenwechsel
- Knie: Totalprothese, Unikompartimentprothese, Prothesenwechsel, Patellofemoralersatz
- Schulter: Totalprothese, Hemiprothese, Prothesenwechsel, inverse Prothese

Osteotomien und Arthrodesen - minimal 15, maximal anrechenbar 50:
- Hüfte: Azetabuläre Osteotomie, proximale Femurosteotomie, Arthrodese
- Knie: Osteotomie, Arthrodese
- Fuss: Osteotomie, Arthrodese
- Wirbelsäule: Spondylodese

Rekonstruktive Eingriffe - minimal 70, maximal anrechenbar 140:
- Schulter: Stabilisation, Rotatorenmanschettenrekonstruktion, Akromioplastik
- Ellbogen: Rekonstruktionen
- Knie: Kreuzbandrekonstruktion, Knorpelrekonstruktion, Meniskuschirurgie

Osteosynthesen - minimal 65, maximal anrechenbar 240:
- Proximales Femur
- Femur
- Patella
- Tibia
- Glenoid
- Humerus
- Radius
- Ulna
- Malleolarfraktur
- Fusswurzel, Fuss
- Handwurzel, Hand

ANATOMIE-PRÜFUNG

Folgende Zugänge werden geprüft:

Upper Extremity:
- Anterior Shoulder (Delto-Pectoral)
- Posterior Shoulder
- Arthroscopic approach of the shoulder
- Humerus Anterior
- Humerus Posterior
- Elbow Medial
- Elbow Lateral (Kocher)
- Radius anterior (Henry)
- Radius posterior (Thompson)
- Dorsal/Palmar distal Radius

Lower Extremity:
- Hip ilio-femoral (Smith Petersen)
- Hip lateral (Watson-Jones)
- Hip transgluteal (Bauer, Hardinge)
- Hip posterior approach (Kocher)
- Knee Medial
- Knee Lateral
- Knee Posterior
- Arthroscopic approach of the knee
- Leg Compartment
- Lateral Ankle
- Medial Ankle
- Dorsal midfoot

SIWF Schweizerisches Institut für ärztliche Weiter- und Fortbildung
ISFM Institut suisse pour la formation médicale postgraduée et continue
FMH | Postfach | 3000 Bern 16 | Telefon +41 31 503 06 00 | info@siwf.ch | www.siwf.ch
"""

def load_orthopedics_content(api_url):
    """Load the pre-extracted orthopedics PDF content"""
    response = requests.post(
        f"{api_url}/api/ingest",
        json={
            'source': 'pdf:orthopaedie-weiterbildung',
            'source_url': 'https://www.siwf.ch/weiterbildung/facharzttitel-und-schwerpunkte/orthopaedie.cfm',
            'title': 'Weiterbildungsprogramm Orthopädische Chirurgie und Traumatologie des Bewegungsapparates',
            'content': ORTHOPEDICS_PDF_CONTENT
        }
    )
    return response.json()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_loader.py <api_url> [pdf_path_or_url]")
        print("       python pdf_loader.py <api_url> --ortho  # Load orthopedics content")
        sys.exit(1)
    
    api_url = sys.argv[1]
    
    if len(sys.argv) > 2:
        if sys.argv[2] == '--ortho':
            result = load_orthopedics_content(api_url)
            print(f"Loaded orthopedics content: {result}")
        else:
            pdf_source = sys.argv[2]
            result = load_pdf_to_api(pdf_source, api_url)
    else:
        # Default: load orthopedics
        result = load_orthopedics_content(api_url)
        print(f"Loaded orthopedics content: {result}")

