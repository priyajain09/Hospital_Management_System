/**********
Initialise MongoDB Database:
**********/
use Hospital_Treatment_Data

db.Treatment.insert({'treat_id' : 0, 'Description' : "Total number of treatments started" 'total_treatments' : 0})

db.Past_Treatments.insert({"time_stamp": new Date() })


/*************
Enter data of Medicine, Disease, Symptom (Postgres)
************/

INSERT INTO medicine
(name)
VALUES
('Combiflame'), ('Paracetamol'), ('Crocin'), ('Volini'), ('Move'),('Liver-52');

INSERT INTO symptom 
(name)
VALUES
('Cold'), ('Fever'), ('Rashes'), ('Vomiting'), ('Sweating'),('Nose Bleeding'),('Nausia');

INSERT INTO disease
(name)
VALUES
('Diabetes'), ('Viral-Fever'), ('Bacterial-Fever'),('Asthenia'), ('Asthma'), ('Astigmatism')('Astrocytoma');

