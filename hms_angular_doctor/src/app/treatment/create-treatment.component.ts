import { Component, OnInit } from '@angular/core';
// Import FormGroup and FormControl classes
import { FormGroup, FormControl, FormBuilder, Validators, FormArray } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { TreatmentService } from './treatment.service';
import { ITreat } from './ITreat';
import { IAllDoct } from './IAllDoct';
import { IPresc } from './IPresc';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-treatment',
  templateUrl: './create-treatment.component.html',
  styleUrls: ['./create-treatment.component.css']
})
export class CreateTreatmentComponent implements OnInit {
  // This FormGroup contains Patient userid and Name form controls
  treatmentForm: FormGroup;
  treatment: ITreat;
  pageTitle: string;
  constructor(private fb: FormBuilder,
              private route: ActivatedRoute,
              private treatmentService: TreatmentService,
              private router: Router) { }

  // Initialise the FormGroup with the 2 FormControls we need.
  // ngOnInit ensures the FormGroup and it's form controls are
  // created when the component is initialised
  ngOnInit() {
    this.treatmentForm = this.fb.group({
      patient_name: [''],
      patient_userid: [''],
      alldoctors: this.fb.array([
        this.addDoctorFormGroup()
      ]
      ),
      start_date: [''],
      time_stamp: [''],
      Referto: [''],

      prescription: this.fb.array([
        this.addPrescriptionFormGroup()
      ])
    });

    // Subscribe to FormGroup valueChanges observable
    this.treatmentForm.valueChanges.subscribe(
    value => {
        console.log(JSON.stringify(value));
      }
    );
    
    this.route.paramMap.subscribe(params => {
      const treatId = +params.get('id');
      if (treatId) {
        this.pageTitle = 'Edit Treatment Details';
        this.getTreatment(treatId);
      }else {
        this.pageTitle = 'Create Treatment';
        this.treatment = {
          id: null,
          patient_name: '',
          patient_userid: '',
          alldoctors: [],
          prescription: [],
          start_date: '',
          time_stamp: '',
          Referto: ''
        };
      }
    });

  }

  getTreatment(id: number) {
    this.treatmentService.getTreatment(id)
      .subscribe(
        (treatment: ITreat) =>{
          this.treatment = treatment;
          this.editTreatment(treatment);
        },
          (err: any) => console.log(err)
      );
  }

  editTreatment(treatment: ITreat) {
    this.treatmentForm.patchValue({

      patient_userid : treatment.patient_userid,
      patient_name : treatment.patient_name,
      start_date : treatment.start_date ,
      time_stamp : treatment.time_stamp,
      Referto: treatment.Referto
      
    });
    this.treatmentForm.setControl('alldoctors', this.setExistingDoctors(treatment.alldoctors));
    this.treatmentForm.setControl('prescription', this.setExistingPrescription(treatment.prescription));
  }
  
  setExistingDoctors(DoctSets: IAllDoct[]): FormArray {
    const formArray = new FormArray([]);
    DoctSets.forEach(s => {
      formArray.push(this.fb.group({
        doctid : s.doctid
      }));
    });

    return formArray;
  }
    setExistingPrescription(PrescSets: IPresc[]): FormArray {
      const formArray = new FormArray([]);
      PrescSets.forEach(s => {
        formArray.push(this.fb.group({
              presid : s.presid,
              date: s.date,
              pres_doctor_userid : s.pres_doctor_userid,
              tests : s.tests,
              symptoms : s.symptoms,
              medicines : s.medicines,
              diet_plan : s.diet_plan,
              next_visit_date : s.next_visit_date
        }));
      });

  
    return formArray;
  }


  addDoctorButtonClick(): void {
    (<FormArray>this.treatmentForm.get('alldoctors')).push(this.addDoctorFormGroup());
  }

  addPrescriptionButtonClick(): void {
    (<FormArray>this.treatmentForm.get('prescription')).push(this.addPrescriptionFormGroup());
  }
  

  addPrescriptionFormGroup(): FormGroup{
    return this.fb.group({
      presid: [''],
      date: [''],
      pres_doctor_userid: [''],
      tests: [''],
      symptoms: [''],
      medicines: [''],
      diet_plan: [''],
      next_visit_date: ['']
    });
  }

  addDoctorFormGroup(): FormGroup{
    return this.fb.group({
      doctid: ['']
    });
  }

  onLoadDataClick(): void {
    this.treatmentForm.patchValue({
      patient_name: 'dsad',
      patient_userid: 'ads',
      alldoctors: {
        doctid: 'asad'
      },
      start_date: 'adssssd',
      time_stamp: 'adsad',
      Referto: 'qwdadad',
      prescription: {
        presid: 'p1234',
        date: 'zcsd',
        pres_doctor_userid: 'd1234',
        tests: 'NIL',
        symptoms: 's123',
        medicines: 'qwqwaas',
        diet_plan: 'dp123',
        next_visit_date: '1march'
      }
    });
  }
  

  logKeyValuePairs(group: FormGroup): void {
    // loop through each key in the FormGroup
    Object.keys(group.controls).forEach((key: string) => {
      // Get a reference to the control using the FormGroup.get() method
      const abstractControl = group.get(key);
      // If the control is an instance of FormGroup i.e a nested FormGroup
      // then recursively call this same method (logKeyValuePairs) passing it
      // the FormGroup so we can get to the form controls in it
      if (abstractControl instanceof FormGroup) {
        this.logKeyValuePairs(abstractControl);
        // If the control is not a FormGroup then we know it's a FormControl
      } else {
        console.log('Key = ' + key + ' && Value = ' + abstractControl.value);
      }
    });
  }

  onSubmit(): void {
    this.mapFormValuesToTreatmentModel();
    if(this.treatment.id){
      this.treatmentService.updateTreatment(this.treatment).subscribe(
      ()=>this.router.navigate(['Show_treatments']),
      (err:any)=>console.log(err)
    );
      }else{
        this.treatmentService.addTreatment(this.treatment).subscribe(
          () => this.router.navigate(['Show_treatments']),
          (err: any) => console.log(err)
        );
      }
  
  }

  mapFormValuesToTreatmentModel() {
    this.treatment.patient_userid = this.treatmentForm.value.patient_userid;
    this.treatment.patient_name = this.treatmentForm.value.patient_name;
    this.treatment.start_date = this.treatmentForm.value.start_date;
    this.treatment.time_stamp = this.treatmentForm.value.time_stamp;
    this.treatment.Referto = this.treatmentForm.value.Referto;
    this.treatment.alldoctors = this.treatmentForm.value.alldoctors;
    this.treatment.prescription = this.treatmentForm.value.prescription;

  }

}