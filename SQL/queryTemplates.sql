#Patient Queries
#By age
select birthDate from `fhir-visualization-project.dataset1.Patient` LIMIT 1000;
#By Gender
SELECT us_core_birthsex.value.code FROM `fhir-visualization-project.dataset1.Patient` LIMIT 1000;
#By birthplace. Maybe for medical tourism purposes/show on a cool map
select patient_birthPlace.value.address from `fhir-visualization-project.dataset1.Patient` LIMIT 1000;
#By Etnicity
select us_core_ethnicity.text.value from `fhir-visualization-project.dataset1.Patient` LIMIT 1000;
#End Patient Queries

#Procedure Queries
#Type of procedure
select code.text from `fhir-visualization-project.dataset1.Procedure`; 
#Time procedure happened, how long it took if you do start-end
select performed.dateTime, performed.period.start, performed.period.end,  from `fhir-visualization-project.dataset1.Procedure`;
#Who sugery was on
select subject.patientId from `fhir-visualization-project.dataset1.Procedure`;

#select subject.identifier.assigner.organizationId from `fhir-visualization-project.dataset1.Procedure` LIMIT 1000;
#select performer[safe_offset(0)].actor.practitionerId as docID, performer[safe_offset(0)].actor.deviceid as equipment, performer[safe_offset(0)].actor.organizationid as organization from `fhir-visualization-project.dataset1.Procedure`;
#select outcome.text from `fhir-visualization-project.dataset1.Procedure`;
#select location.locationid from `fhir-visualization-project.dataset1.Procedure`;
#select bodySite[safe_offset(0)].text from `fhir-visualization-project.dataset1.Procedure`; 
#select r.procedureId from `fhir-visualization-project.dataset1.Procedure`, unnest(reasonReference) as r LIMIT 1000;

#End Procedure Queries

#Practitioner Queries
#Gender
select gender from `fhir-visualization-project.dataset1.Practitioner` LIMIT 1000;
#Address
select a.city, a.postalCode, a.state from `fhir-visualization-project.dataset1.Practitioner`, unnest(address) as a LIMIT 1000;
#select birthDate from `fhir-visualization-project.dataset1.Practitioner` LIMIT 1000;
#select qualification[safe_offset(0)].period.end,  qualification[safe_offset(0)].identifier[safe_offset(0)].type.text 
#from `fhir-visualization-project.dataset1.Practitioner` LIMIT 1000;
#SELECT  id.assigner.identifier.period.start FROM  `fhir-visualization-project.dataset1.Practitioner`, UNNEST(identifier) AS id
#End Practitioner Queries

#Begin Medication Request Queries
#Doctor Ordering Meds
select requester.display from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;
#Who the Meds are for
select subject.patientId from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;
#The type of medication ordered
select medication.codeableConcept.text from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;
#The status of the request (active,stop,pause)
select status from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;
#When the request was sent in
select authoredOn from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;

#select insurance[SAFE_OFFSET(0)].coverageId from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;
#select priority from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;
#select medication.reference.medicationId from `fhir-visualization-project.dataset1.MedicationRequest` LIMIT 1000;
# End Medication Request Queries

#Condition Queries
#Get Patient
select subject.patientId from `fhir-visualization-project.dataset1.Condition` LIMIT 1000;
#Find current conditions
select code.text from `fhir-visualization-project.dataset1.Condition` LIMIT 1000;
#Status of Condition - active resolved inactive
SELECT coding.code FROM  `fhir-visualization-project.dataset1.Condition`, UNNEST(clinicalStatus.coding) AS coding LIMIT 1000;
#Show current conditions, and how the condition was found.
SELECT 
  encounter_type.text as FoundBecauseOf,
  condition.code.text as CurrentCondition
FROM 
  `fhir-visualization-project.dataset1.Condition` AS condition
JOIN 
  `fhir-visualization-project.dataset1.Encounter` AS encounter
ON 
  encounter.id = condition.encounter.encounterId
CROSS JOIN 
  UNNEST(encounter.type) AS encounter_type;


#select severity.text from `fhir-visualization-project.dataset1.Condition` LIMIT 1000;
#select clinicalStatus.text from `fhir-visualization-project.dataset1.Condition` LIMIT 1000;
#select bodySite[safe_offset(0)].text from `fhir-visualization-project.dataset1.Condition` LIMIT 1000;
#End condition Queries

#Claim Queries
#Type of claim
select c.code as claimType from `fhir-visualization-project.dataset1.Claim`, unnest(type.coding) as c LIMIT 1000;
#When status of cliam (active,inactive,pause) when it was created, when the date it must be payed by
select status, created, billablePeriod.end as BillablePeriodEnd from `fhir-visualization-project.dataset1.Claim` LIMIT 1000;
#Reason for the claim
select i.productOrService.text as ReasonForClaim from `fhir-visualization-project.dataset1.Claim`, unnest(item) as i LIMIT 1000;
#Show insurance providers and coverage they provide
SELECT 
  provider.display as InsuranceProvider, 
  i.coverage.display as CoverageType 
FROM 
  `fhir-visualization-project.dataset1.Claim`,
  UNNEST(insurance) AS i 
GROUP BY 
  provider.display, i.coverage.display 
LIMIT 1000;
#Total $ 
SELECT SUM(total.value) AS total_sum
FROM `fhir-visualization-project.dataset1.Claim`
where status = 'Active';
#End Claim Queries
