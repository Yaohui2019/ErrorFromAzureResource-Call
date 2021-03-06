def sample_analyze_healthcare_entities():
    print(
        "In this sample we will be combing through the prescriptions our pharmacy has fulfilled "
        "so we can catalog how much inventory we have"
    )
    print(
        "We start out with a list of prescription documents."
    )

    # [START analyze_healthcare_entities]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient, HealthcareEntityRelation

    # endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    # key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]
    endpoint = os.environ["https://trial-8-4.cognitiveservices.azure.com/"]
    key = os.environ["4569944db10141d38e21c0cbf71b6195"]


    text_analytics_client = TextAnalyticsClient(endpoint= endpoint,credential = AzureKeyCredential(key))

    documents = [
        """
        Patient needs to take 100 mg of ibuprofen, and 3 mg of potassium. Also needs to take
        10 mg of Zocor.
        """,
        """
        Patient needs to take 50 mg of ibuprofen, and 2 mg of Coumadin.
        """
    ]

    poller = text_analytics_client.begin_analyze_healthcare_entities(documents)
    result = poller.result()

    docs = [doc for doc in result if not doc.is_error]

    print("Let's first visualize the outputted healthcare result:")
    for idx, doc in enumerate(docs):
        for entity in doc.entities:
            print("Entity: {}".format(entity.text))
            print("...Normalized Text: {}".format(entity.normalized_text))
            print("...Category: {}".format(entity.category))
            print("...Subcategory: {}".format(entity.subcategory))
            print("...Offset: {}".format(entity.offset))
            print("...Confidence score: {}".format(entity.confidence_score))
            if entity.data_sources is not None:
                print("...Data Sources:")
                for data_source in entity.data_sources:
                    print("......Entity ID: {}".format(data_source.entity_id))
                    print("......Name: {}".format(data_source.name))
            if entity.assertion is not None:
                print("...Assertion:")
                print("......Conditionality: {}".format(entity.assertion.conditionality))
                print("......Certainty: {}".format(entity.assertion.certainty))
                print("......Association: {}".format(entity.assertion.association))
        for relation in doc.entity_relations:
            print("Relation of type: {} has the following roles".format(relation.relation_type))
            for role in relation.roles:
                print("...Role '{}' with entity '{}'".format(role.name, role.entity.text))
        print("------------------------------------------")

    print("Now, let's get all of medication dosage relations from the documents")
    dosage_of_medication_relations = [
        entity_relation
        for doc in docs
        for entity_relation in doc.entity_relations if entity_relation.relation_type == HealthcareEntityRelation.DOSAGE_OF_MEDICATION
    ]
    # [END analyze_healthcare_entities]

    print(
        "Now, I will create a dictionary of medication to total dosage. "
        "I will use a regex to extract the dosage amount. For simplicity sake, I will assume "
        "all dosages are represented with numbers and have mg unit."
    )
    import re
    from collections import defaultdict

    medication_to_dosage = defaultdict(int)

    for relation in dosage_of_medication_relations:
        # The DosageOfMedication relation should only contain the dosage and medication roles

        dosage_role = next(iter(filter(lambda x: x.name == "Dosage", relation.roles)))
        medication_role = next(iter(filter(lambda x: x.name == "Medication", relation.roles)))

        try:
            dosage_value = int(re.findall(r"\d+", dosage_role.entity.text)[0]) # we find the numbers in the dosage
            medication_to_dosage[medication_role.entity.text] += dosage_value
        except StopIteration:
            # Error handling for if there's no dosage in numbers.
            pass

    for medication, dosage in medication_to_dosage.items():
        print("We have fulfilled '{}' total mg of '{}'".format(
            dosage, medication
        ))


if __name__ == "__main__":
    sample_analyze_healthcare_entities()