from presidio_analyzer import (
    AnalyzerEngine, 
    PatternRecognizer, 
    Pattern
)
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def add_custom_recognizer():
    # Create Pattern object
    emp_pattern = Pattern(
        name="EmployeeID", 
        regex=r"EmployeeID\s*\d+", 
        score=0.85
    )

    # Pass list of Pattern objects
    emp_id_recognizer = PatternRecognizer(
        supported_entity="EMPLOYEE_ID",
        patterns=[emp_pattern]
    )

    manager_id_pattern = Pattern(
        name="ManagerID", 
        regex=r"ManagerID\s*\d+", 
        score=0.85
    )

    manager_id_recognizer = PatternRecognizer(
        supported_entity="MANAGER_ID",
        patterns=[manager_id_pattern]
    )

    analyzer.registry.add_recognizer(emp_id_recognizer)
    analyzer.registry.add_recognizer(manager_id_recognizer)


def presidio_post_process(user_role: str, text: str) -> str:
    if(user_role.lower()=="admin"):
        return text
    if(user_role.lower()=="public"):
        add_custom_recognizer()

    results = analyzer.analyze(text=text, language='en')
    if not results:
        return text
    
    #Printing for now, later will help in logging
    for entity in results:
        print(f"Detected {entity.entity_type} at {entity.start}-{entity.end}")
    
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_result.text
