import { Component, OnInit } from '@angular/core';
import { TreatmentService } from './treatment.service';
import { ITreat } from './ITreat';
import { Router } from '@angular/router';

@Component({
  selector: 'app-list-treatment',
  templateUrl: './list-treatment.component.html',
  styleUrls: ['./list-treatment.component.css']
})
export class ListTreatmentsComponent implements OnInit {
  treatments: ITreat[];

  
  constructor(private _treatmentService: TreatmentService,
    private _router: Router) { }

  ngOnInit() {
    this._treatmentService.getTreatments().subscribe(
      (treatmentList) => this.treatments = treatmentList,
      (err) => console.log(err)
    );
  }

  editButtonClick(treatmentId: number) {
    this._router.navigate(['/edit', treatmentId]);
  }

}
