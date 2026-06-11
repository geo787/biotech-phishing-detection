from main import load_csv
from nlp_module import NLPDetector
from analyzers import EpicAnalyzer, CernerAnalyzer, MedidataAnalyzer

texts, labels, urls, software_types = load_csv('data/emails_medical.csv')
print('Loaded', len(texts), 'rows')

nlp = NLPDetector()
nlp.train(texts, labels)
ANALYZERS = {'epic': EpicAnalyzer(), 'cerner': CernerAnalyzer(), 'medidata': MedidataAnalyzer()}

for i in range(len(texts)):
    s = (software_types[i] if i < len(software_types) else 'generic').lower()
    if s in ANALYZERS:
        a = ANALYZERS[s]
        print(f"Row {i+1}: analyzer={s} ->", a.analyze(texts[i], urls[i]))
    else:
        print(f"Row {i+1}: generic -> NLP={nlp.predict(texts[i])}")
