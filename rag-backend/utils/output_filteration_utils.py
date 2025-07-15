from presidio_analyzer import (
    AnalyzerEngine, 
    PatternRecognizer, 
    Pattern
)
from presidio_anonymizer import AnonymizerEngine
from openai import OpenAI

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


def presidio_post_process(user_role: str, user_name: str, text: str) -> str:
    if(user_role.lower()=="admin"):
        return text
    
    add_custom_recognizer()
    results = analyzer.analyze(text=text, language='en')
    if not results:
        return text
    
    if(user_role.lower()=="employee"):
        filtered_results = []
    
        for entity in results:
            entity_text = text[entity.start:entity.end]

            # Skip redacting the employee's own name
            if entity.entity_type == "PERSON" and user_name.lower() in entity_text.lower():
                    print(f"Skipping redaction for user_name match: {entity_text}")
                    continue
            filtered_results.append(entity)
        results=filtered_results

    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_result.text

def is_flagged_by_openai_moderation(result):
    client = OpenAI()
    response = client.moderations.create(input=result)
    return response.results[0].flagged