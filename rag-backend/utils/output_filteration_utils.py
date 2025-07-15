from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def presidio_post_process(text: str) -> str:
    results = analyzer.analyze(text=text, language='en')
    if not results:
        return text
    
    #Printing for now, later will help in logging
    for entity in results:
        print(f"Detected {entity.entity_type} at {entity.start}-{entity.end}")
    
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_result.text
