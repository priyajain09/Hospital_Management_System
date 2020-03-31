import { Component, OnInit } from '@angular/core';
import { HomeService } from './home.service';
import { IDoctor } from './IDoctor';
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  doctors: IDoctor[];
  constructor(private _homeService: HomeService) { }

  ngOnInit(): void {
    this._homeService.getDoctors().subscribe(
      (doctorList) => this.doctors = doctorList,
      (err) => console.log(err)
    );
  }

}
